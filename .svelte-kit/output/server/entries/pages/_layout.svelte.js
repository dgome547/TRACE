import { d as slot } from "../../chunks/index.js";
function _layout($$payload, $$props) {
  $$payload.out += `<main><!---->`;
  slot($$payload, $$props, "default", {});
  $$payload.out += `<!----></main> <footer></footer>`;
}
export {
  _layout as default
};
