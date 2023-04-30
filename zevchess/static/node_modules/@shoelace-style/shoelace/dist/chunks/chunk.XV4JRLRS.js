import {
  SlTextarea
} from "./chunk.IXPLTYT4.js";

// src/react/textarea/index.ts
import * as React from "react";
import { createComponent } from "@lit-labs/react";
var textarea_default = createComponent({
  tagName: "sl-textarea",
  elementClass: SlTextarea,
  react: React,
  events: {
    onSlBlur: "sl-blur",
    onSlChange: "sl-change",
    onSlFocus: "sl-focus",
    onSlInput: "sl-input",
    onSlInvalid: "sl-invalid"
  }
});

export {
  textarea_default
};
