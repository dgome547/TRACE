import { e as ensure_array_like, c as pop, p as push } from "../../../chunks/index.js";
import { e as escape_html } from "../../../chunks/escaping.js";
function _page($$payload, $$props) {
  push();
  let credentials = [];
  $$payload.out += `<section class="svelte-5kknpe"><div class="card svelte-5kknpe"><h2 class="svelte-5kknpe">Simulated ML Algorithm - Credential Generator</h2> <button class="svelte-5kknpe">Generate Credentials</button> <div class="results svelte-5kknpe"><h3>Generated Credentials</h3> `;
  if (credentials.length > 0) {
    $$payload.out += "<!--[-->";
    const each_array = ensure_array_like(credentials);
    $$payload.out += `<ul><!--[-->`;
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let cred = each_array[$$index];
      $$payload.out += `<li><strong>URL:</strong> ${escape_html(cred.url)}<br> <strong>Username:</strong> ${escape_html(cred.username)}<br> <strong>Password:</strong> ${escape_html(cred.password)}<br><br></li>`;
    }
    $$payload.out += `<!--]--></ul>`;
  } else {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]--></div></div></section>`;
  pop();
}
export {
  _page as default
};
