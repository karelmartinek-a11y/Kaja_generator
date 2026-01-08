export const END_OF_SPEC_MARKER_ID: string = "MASTER_SPEC_END_MARKER";

export function isEndOfSpecChunk(chunkId: string): boolean {
  return chunkId === END_OF_SPEC_MARKER_ID;
}
