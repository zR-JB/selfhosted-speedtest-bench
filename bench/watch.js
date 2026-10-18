// Moves pins.json to every tool's, client's and browser's newest release, with fresh digests and checksums, and
// prints what changed as Markdown: node bench/watch.js > changes.md
import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

const file = new URL("../pins.json", import.meta.url);
const pins = JSON.parse(readFileSync(file, "utf8"));
const changes = [];

async function get(url, init = {}) {
  const response = await fetch(url, { ...init, signal: AbortSignal.timeout(300_000) });
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response;
}
const json = (url, headers) => get(url, { headers }).then((r) => r.json());
const github = (path) =>
  json(`https://api.github.com/${path}`, process.env.GITHUB_TOKEN ? { authorization: `Bearer ${process.env.GITHUB_TOKEN}` } : {});
const sha256 = async (url) =>
  createHash("sha256").update(Buffer.from(await (await get(url)).arrayBuffer())).digest("hex");
const fill = (template, version) => template.replaceAll("{version}", version);

const REGISTRIES = {
  "ghcr.io": { host: "ghcr.io", token: (repo) => `https://ghcr.io/token?scope=repository:${repo}:pull` },
  "docker.io": {
    host: "registry-1.docker.io",
    token: (repo) => `https://auth.docker.io/token?service=registry.docker.io&scope=repository:${repo}:pull`,
  },
};
async function digest(ref) {
  const [, registry, repo, tag] = /^([^/]+)\/(.+):([^:@]+)$/.exec(ref);
  const { host, token } = REGISTRIES[registry];
  const response = await get(`https://${host}/v2/${repo}/manifests/${tag}`, {
    method: "HEAD",
    headers: {
      authorization: `Bearer ${(await json(token(repo))).token}`,
      accept: "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json",
    },
  });
  return response.headers.get("docker-content-digest");
}

async function watch(name, entry) {
  const rule = entry.watch;
  const version = rule.github
    ? (await github(`repos/${rule.github}/releases/latest`)).tag_name.replace(/^v/, "")
    : entry.version;
  if (rule.image) {
    const ref = fill(rule.image, version);
    const image = `${ref}@${await digest(ref)}`;
    if (version === entry.version && image === entry.image) return;
    changes.push(`- ${entry.name}: ${entry.version} → ${version}, image ${image}`);
    Object.assign(entry, { version, image });
    return;
  }
  if (version === entry.version) return;
  const url = fill(rule.release, version);
  entry.release = { ...entry.release, url, sha256: await sha256(url), command: rule.command?.map((part) => fill(part, version)) ?? entry.release.command };
  changes.push(`- ${entry.name}: ${entry.version} → ${version}`);
  entry.version = version;
}

async function browser(name, entry, version, url, sha) {
  if (version === entry.version) return;
  changes.push(`- ${name}: ${entry.version} → ${version}`);
  Object.assign(entry, { version, url, sha256: await sha });
}

for (const [name, entry] of Object.entries({ ...pins.tools, ...pins.clients }))
  if (entry.watch) await watch(name, entry);

const chrome = (await json("https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json")).channels
  .Stable.version;
const chromeUrl = `https://storage.googleapis.com/chrome-for-testing-public/${chrome}/linux64/chrome-linux64.zip`;
await browser("Chrome for Testing", pins.browsers.chrome, chrome, chromeUrl, chrome === pins.browsers.chrome.version ? null : sha256(chromeUrl));

const firefox = (await json("https://product-details.mozilla.org/1.0/firefox_versions.json")).LATEST_FIREFOX_VERSION;
const firefoxUrl = `https://ftp.mozilla.org/pub/firefox/releases/${firefox}/linux-x86_64/en-US/firefox-${firefox}.tar.xz`;
// Mozilla publishes the checksum, so the archive is only downloaded later, by the run that verifies it.
const firefoxSha = async () =>
  (await (await get(`https://ftp.mozilla.org/pub/firefox/releases/${firefox}/SHA256SUMS`)).text())
    .split("\n")
    .find((line) => line.endsWith(` linux-x86_64/en-US/firefox-${firefox}.tar.xz`))
    ?.split(" ")[0];
await browser("Firefox", pins.browsers.firefox, firefox, firefoxUrl, firefox === pins.browsers.firefox.version ? null : firefoxSha());

if (changes.length) writeFileSync(file, `${JSON.stringify(pins, null, 2)}\n`);
console.log(changes.length ? `New releases:\n\n${changes.join("\n")}` : "No new releases.");
