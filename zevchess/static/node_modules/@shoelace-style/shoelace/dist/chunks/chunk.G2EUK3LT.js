import {
  SlCarousel
} from "./chunk.TDXYRAD2.js";

// src/react/carousel/index.ts
import * as React from "react";
import { createComponent } from "@lit-labs/react";
var carousel_default = createComponent({
  tagName: "sl-carousel",
  elementClass: SlCarousel,
  react: React,
  events: {
    onSlSlideChange: "sl-slide-change"
  }
});

export {
  carousel_default
};
