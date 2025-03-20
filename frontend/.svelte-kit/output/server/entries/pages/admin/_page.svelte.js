import { e as ensure_array_like, c as pop, p as push } from "../../../chunks/index.js";
import "../../../chunks/client.js";
import { a as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$payload, $$props) {
  push();
  let attackTypes = ["webcrawler", "Bruteforcer", "ML Algorithm"];
  const each_array = ensure_array_like(attackTypes);
  $$payload.out += `<main class="container svelte-c75d4e"><div class="island svelte-c75d4e"><label for="attack-select">Select an Option:</label> <select id="attack-select" class="svelte-c75d4e"><option value="" disabled selected>Select...</option><!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let type = each_array[$$index];
    $$payload.out += `<option${attr("value", type)}>${escape_html(type)}</option>`;
  }
  $$payload.out += `<!--]--></select> <button class="svelte-c75d4e">Go</button></div></main>`;
  pop();
}
export {
  _page as default
};
