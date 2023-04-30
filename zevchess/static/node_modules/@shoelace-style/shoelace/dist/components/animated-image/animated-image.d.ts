import '../icon/icon';
import ShoelaceElement from '../../internal/shoelace-element';
import type { CSSResultGroup } from 'lit';
export default class SlAnimatedImage extends ShoelaceElement {
    static styles: CSSResultGroup;
    animatedImage: HTMLImageElement;
    frozenFrame: string;
    isLoaded: boolean;
    src: string;
    alt: string;
    play: boolean;
    private handleClick;
    private handleLoad;
    private handleError;
    handlePlayChange(): void;
    handleSrcChange(): void;
    render(): import("lit-html").TemplateResult<1>;
}
declare global {
    interface HTMLElementTagNameMap {
        'sl-animated-image': SlAnimatedImage;
    }
}
