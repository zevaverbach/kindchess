import {
  SlTag
} from "./chunk.NXSD2QGE.js";

// src/react/tag/index.ts
import * as React from "react";
import { createComponent } from "@lit-labs/react";
var tag_default = createComponent({
  tagName: "sl-tag",
  elementClass: SlTag,
  react: React,
  events: {
    onSlRemove: "sl-remove"
  }
});

export {
  tag_default
};
