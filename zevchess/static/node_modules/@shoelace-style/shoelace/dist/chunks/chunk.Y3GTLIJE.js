import {
  SlInput
} from "./chunk.R4E7437B.js";

// src/react/input/index.ts
import * as React from "react";
import { createComponent } from "@lit-labs/react";
var input_default = createComponent({
  tagName: "sl-input",
  elementClass: SlInput,
  react: React,
  events: {
    onSlBlur: "sl-blur",
    onSlChange: "sl-change",
    onSlClear: "sl-clear",
    onSlFocus: "sl-focus",
    onSlInput: "sl-input",
    onSlInvalid: "sl-invalid"
  }
});

export {
  input_default
};
