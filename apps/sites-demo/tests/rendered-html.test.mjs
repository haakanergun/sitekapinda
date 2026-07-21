import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the fictional noindex customer preview", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Sedirra — A fictional neighborhood kitchen demo<\/title>/i);
  assert.match(
    html,
    /<meta(?=[^>]*\bname=["']robots["'])(?=[^>]*\bcontent=["']noindex, nofollow["'])[^>]*>/i,
  );
  assert.match(html, /Fictional customer preview/);
  assert.match(html, /Concept imagery created for this rights-safe demo\./);
  assert.match(html, /No real address, phone number, or booking system is connected/);
  assert.match(html, /This is the first version—not the final launch\./);
  assert.match(html, /Customer revisions/);
  assert.match(html, /Approval/);
  assert.match(html, /Custom domain/);
  assert.doesNotMatch(html, /href=["'](?:mailto:|tel:)/i);
  assert.doesNotMatch(html, /<form\b/i);
});

test("keeps the submitted source fictional and deployment-neutral", async () => {
  const [page, layout, hosting] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../.openai/hosting.json", import.meta.url), "utf8"),
  ]);

  assert.match(page, /Fictional customer preview/);
  assert.match(page, /No real address, phone number, or booking system/);
  assert.match(page, /explicitly approves the version/);
  assert.match(layout, /robots:\s*\{\s*index:\s*false,\s*follow:\s*false\s*\}/);

  const hostingConfig = JSON.parse(hosting);
  assert.equal(hostingConfig.project_id, "local-demo-not-deployable");
  assert.equal(hostingConfig.d1, null);
  assert.equal(hostingConfig.r2, null);

  await access(new URL("../public/sedirra-hero.png", import.meta.url));
  await access(new URL("../public/og.png", import.meta.url));
});
