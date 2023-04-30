import type { ShoelaceFormControl } from '../shoelace-element';
export declare function runFormControlBaseTests<T extends ShoelaceFormControl = ShoelaceFormControl>(tagNameOrConfig: string | {
    tagName: string;
    init?: (control: T) => void;
    variantName: string;
}): void;
