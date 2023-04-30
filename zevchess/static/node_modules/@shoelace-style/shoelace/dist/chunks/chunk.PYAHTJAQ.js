import {
  SlRadioGroup
} from "./chunk.PNUSZ2JQ.js";

// src/react/radio-group/index.ts
import * as React from "react";
import { createComponent } from "@lit-labs/react";
var radio_group_default = createComponent({
  tagName: "sl-radio-group",
  elementClass: SlRadioGroup,
  react: React,
  events: {
    onSlChange: "sl-change",
    onSlInput: "sl-input",
    onSlInvalid: "sl-invalid"
  }
});

export {
  radio_group_default
};
