/** Single byte ranges used by browser video players; no whole-file buffering. */
export function videoRange(header: string, size: number): {start: number; end: number} | "unsatisfiable" | null {
  const match = /^bytes=(\d*)-(\d*)$/.exec(header.trim());
  // Unsupported/malformed/multipart ranges are ignored, as allowed by HTTP.
  if (!match || (!match[1] && !match[2])) return null;
  const a = Number(match[1]), b = Number(match[2]);
  if (!Number.isSafeInteger(a) || !Number.isSafeInteger(b)) return null;
  const start = match[1] ? a : Math.max(0, size - b);
  const end = match[1] && match[2] ? Math.min(b, size - 1) : size - 1;
  if (start >= size || end < start || (!match[1] && b === 0)) return "unsatisfiable";
  return {start, end};
}

export function sliceVideo(source: ReadableStream<Uint8Array>, start: number, end: number): ReadableStream<Uint8Array> {
  const reader = source.getReader();
  let offset = 0;
  return new ReadableStream<Uint8Array>({
    async pull(controller) {
      try {
        while (true) {
          const {done, value} = await reader.read();
          if (done) throw new Error("Show asset ended before its advertised range");
          const next = offset + value.byteLength;
          if (next > start) {
            const bytes = value.subarray(Math.max(0, start - offset), Math.min(value.byteLength, end + 1 - offset));
            offset = next;
            controller.enqueue(bytes);
            if (next > end) { controller.close(); await reader.cancel(); }
            return;
          }
          offset = next;
        }
      } catch (error) {
        controller.error(error);
        await reader.cancel(error);
      }
    },
    cancel(reason) { return reader.cancel(reason); },
  });
}
