import {
  SlTooltip
} from "./chunk.LJX6BXHL.js";

// src/react/tooltip/index.ts
import * as React from "react";
import { createComponent } from "@lit-labs/react";
var tooltip_default = createComponent({
  tagName: "sl-tooltip",
  elementClass: SlTooltip,
  react: React,
  events: {
    onSlShow: "sl-show",
    onSlAfterShow: "sl-after-show",
    onSlHide: "sl-hide",
    onSlAfterHide: "sl-after-hide"
  }
});

export {
  tooltip_default
};
