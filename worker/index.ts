/** Cloudflare Worker entry point for The Long Game. */
import handler from "vinext/server/app-router-entry";
import {sliceVideo, videoRange} from "./video-range";
import release from "../docs/releases/show-media-current.json";

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const pathname = new URL(request.url).pathname;
    if ((request.method === "GET" || request.method === "HEAD") &&
        (pathname === "/show/pilot-review.mp4" || /^\/show\/previews\/[^/]+\.mp4$/.test(pathname))) {
      const headers = new Headers(request.headers);
      headers.delete("Range"); headers.delete("If-Range");
      const asset = await env.ASSETS.fetch(new Request(request, {headers}));
      if (asset.status !== 200) return asset;
      const responseHeaders = new Headers(asset.headers);
      responseHeaders.set("Accept-Ranges", "bytes");
      // The internal asset binding can omit Content-Length even though the
      // public asset response adds it. The current bounded release files have
      // checksummed lengths verified before deployment; unknown files do not.
      const declaredSize = Number(asset.headers.get("Content-Length"));
      const knownSize = release.media.find(item => item.video === pathname)?.bytes ?? 0;
      const size = declaredSize || knownSize;
      const rangeHeader = request.headers.get("Range");
      const ifRange = request.headers.get("If-Range");
      const validValidator = !ifRange || (ifRange === asset.headers.get("ETag") && !ifRange.startsWith("W/"));
      if (request.method === "GET" && rangeHeader && validValidator && asset.body &&
          Number.isSafeInteger(size) && size > 0 && size <= 25 * 1024 * 1024) {
        const range = videoRange(rangeHeader, size);
        if (range === "unsatisfiable") {
          await asset.body.cancel();
          responseHeaders.set("Content-Range", `bytes */${size}`);
          responseHeaders.delete("Content-Length");
          return new Response(null, {status: 416, headers: responseHeaders});
        }
        if (range) {
          const length = range.end - range.start + 1;
          // A Workers fixed-length stream preserves the numeric Content-Length;
          // stream only the requested interval and cancel the remainder.
          const fixed = new FixedLengthStream(length);
          ctx.waitUntil(sliceVideo(asset.body, range.start, range.end).pipeTo(fixed.writable));
          responseHeaders.set("Content-Length", String(length));
          responseHeaders.set("Content-Range", `bytes ${range.start}-${range.end}/${size}`);
          return new Response(fixed.readable, {status: 206, headers: responseHeaders});
        }
      }
      return new Response(asset.body, {status: asset.status, headers: responseHeaders});
    }
    return handler.fetch(request, env, ctx);
  },
} satisfies ExportedHandler<Env>;
