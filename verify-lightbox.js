// Hidden spoilers and closed gallery groups must stay outside a screening sequence.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const handlers = () => ({handlers: {}, hidden: false, textContent: '',
  addEventListener(type, fn) { this.handlers[type] = fn; },
  focus() { document.activeElement = this; }});
const openGroup = {tagName: 'DETAILS', open: true};
const closedSpoiler = {tagName: 'DETAILS', open: false, parentElement: openGroup};
const closedGroup = {tagName: 'DETAILS', open: false};
const links = [openGroup, closedSpoiler, openGroup, closedGroup].map((parentElement, index) => ({
  ...handlers(), parentElement, href: `/assets/media/image-${index}.jpg`,
  querySelector() { return {alt: `image ${index}`}; },
}));
let box;
const elements = Object.fromEntries(['img', '.lb-count', '.lb-original', '.lb-prev', '.lb-next', '.lb-close'].map(key => [key, handlers()]));
const regions = [{}, {}, {}];
const document = {
  body: {classList: {contains: () => true, add() {}, remove() {}}, append(value) { value.isConnected = true; }},
  querySelectorAll(selector) { return selector.startsWith('main ') ? links : regions; },
  createElement() {
    box = {...handlers(), isConnected: false, setAttribute() {}, querySelector(key) { return elements[key]; }, remove() { this.isConnected = false; }};
    return box;
  },
};
vm.runInNewContext(fs.readFileSync(`${__dirname}/tas-lightbox.js`, 'utf8'), {document, window: {addEventListener() {}}});
function click(link, extra = {}) {
  const event = {button: 0, defaultPrevented: false, preventDefault() { this.prevented = true; }, ...extra};
  link.handlers.click(event); return event;
}
assert.equal(click(links[0], {ctrlKey: true}).prevented, undefined);
assert.equal(box, undefined);
assert.equal(click(links[0]).prevented, true);
assert.equal(elements['.lb-count'].textContent, '01 / 02');
assert.equal(elements['.lb-original'].href, links[0].href);
elements['.lb-next'].handlers.click();
assert.equal(elements['.lb-original'].href, links[2].href);
elements['.lb-next'].handlers.click();
assert.equal(elements['.lb-original'].href, links[0].href);
assert.ok(regions.every(region => region.inert));
box.handlers.keydown({key: 'Escape'});
assert.equal(box.isConnected, false);
assert.equal(document.activeElement, links[0]);
assert.ok(regions.every(region => !region.inert));
closedSpoiler.open = true;
click(links[1]);
assert.equal(elements['.lb-count'].textContent, '02 / 03');
assert.equal(elements['.lb-original'].href, links[1].href);
assert.equal(elements.img.alt, 'image 1');
box.handlers.keydown({key: 'ArrowRight'});
assert.equal(elements['.lb-original'].href, links[2].href);
box.handlers.keydown({key: 'ArrowLeft'});
assert.equal(elements['.lb-original'].href, links[1].href);
elements['.lb-close'].handlers.click();
closedSpoiler.open = false;
click(links[0]);
assert.equal(elements['.lb-count'].textContent, '01 / 02');
console.log('PASS: closed spoilers/groups excluded; explicit reveals, next/previous, Escape, focus restoration and modified-link fallback');
