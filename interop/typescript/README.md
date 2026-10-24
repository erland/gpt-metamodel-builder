# Independent TypeScript MMP 1.0.0 consumer

This is a separate read-only implementation. It does **not** call or translate the Python consumer. Node 22+ is recommended.

```sh
npm ci
npm run build
node dist/consumer.js path/to/model.mmp.zip
node dist/conformance.js path/to/mmp-specification-1.0.0.zip
```

It validates a ZIP's member names, inventory, hashes, required canonical documents, JSON Schema (using embedded offline schemas), model identity, type-ID uniqueness, inheritance cycles, endpoint references and property references. It does not implement Rules/Notation/Viewpoints profiles or assert full MMP Core 1.1 conformance. A rejected package exits nonzero. The conformance runner prints each of the nine baseline cases and returns nonzero on any mismatch.
