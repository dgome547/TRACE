import { e as ensure_array_like, c as pop, p as push } from "../../chunks/index.js";
import "../../chunks/client.js";
import { e as escape_html } from "../../chunks/escaping.js";
function _page($$payload, $$props) {
  push();
  let userTypes = [
    { label: "Admin", value: "admin" },
    { label: "User", value: "user" },
    { label: "Guest", value: "guest" }
  ];
  const each_array = ensure_array_like(userTypes);
  $$payload.out += `<section class="flex flex-col items-center justify-center min-h-screen bg-gray-100 svelte-18955ys"><div class="bg-white p-8 rounded-2xl shadow-lg w-80"><h2 class="text-2xl font-semibold mb-4 text-center">Select User Type</h2> <div class="flex flex-col space-y-4"><!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let user = each_array[$$index];
    $$payload.out += `<button class="bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">${escape_html(user.label)}</button>`;
  }
  $$payload.out += `<!--]--></div></div></section>`;
  pop();
}
export {
  _page as default
};
