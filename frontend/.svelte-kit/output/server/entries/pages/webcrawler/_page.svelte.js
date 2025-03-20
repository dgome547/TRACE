import { a as attr } from "../../../chunks/attributes.js";
import { e as escape_html } from "../../../chunks/escaping.js";
import { c as pop, p as push } from "../../../chunks/index.js";
import "../../../chunks/client.js";
function _page($$payload, $$props) {
  push();
  let url = "";
  let depthLimit = 1;
  let timeout = 5e3;
  let loading = false;
  $$payload.out += `<section class="svelte-1gqsgp7"><div class="card svelte-1gqsgp7"><h2 class="svelte-1gqsgp7">Crawler Configuration</h2> <label for="crawler-url" class="svelte-1gqsgp7">URL</label> <input id="crawler-url" type="text"${attr("value", url)} placeholder="https://example.com" class="svelte-1gqsgp7"> <label for="crawler-depth" class="svelte-1gqsgp7">Depth Limit</label> <input id="crawler-depth" type="number"${attr("value", depthLimit)} class="svelte-1gqsgp7"> <label for="crawler-timeout" class="svelte-1gqsgp7">Timeout (ms)</label> <input id="crawler-timeout" type="number"${attr("value", timeout)} class="svelte-1gqsgp7"> <button${attr("disabled", loading, true)} class="svelte-1gqsgp7">${escape_html("Start Crawler")}</button> `;
  {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]--> `;
  {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]--></div></section>`;
  pop();
}
export {
  _page as default
};
