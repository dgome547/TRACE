import { e as ensure_array_like, c as pop, p as push } from "../../chunks/index.js";
import { e as escape_html } from "../../chunks/client.js";
import "clsx";
const replacements = {
  translate: /* @__PURE__ */ new Map([
    [true, "yes"],
    [false, "no"]
  ])
};
function attr(name, value, is_boolean = false) {
  if (value == null || !value && is_boolean) return "";
  const normalized = name in replacements && replacements[name].get(value) || value;
  const assignment = is_boolean ? "" : `="${escape_html(normalized, true)}"`;
  return ` ${name}${assignment}`;
}
function _page($$payload, $$props) {
  push();
  let attackTypes = ["Webcrawler", "Bruteforcer", "ML Algorithm"];
  const each_array = ensure_array_like(attackTypes);
  $$payload.out += `<main class="container svelte-1cif63y"><div class="island svelte-1cif63y"><label for="attack-select">Select an Option:</label> <select id="attack-select" class="svelte-1cif63y"><option value="" disabled selected>Select...</option><!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let type = each_array[$$index];
    $$payload.out += `<option${attr("value", type)}>${escape_html(type)}</option>`;
  }
  $$payload.out += `<!--]--></select> <button class="svelte-1cif63y">Go</button></div></main>`;
  pop();
}
export {
  _page as default
};
