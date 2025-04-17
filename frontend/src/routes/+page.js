// // src/routes/+page.js
// export async function load() {
//     try {
//         const response = await fetch('http://127.0.0.1:5000/api/friends');
//         if (!response.ok) {
//             throw new Error(`Failed to fetch friends data: ${response.status}`);
//         }
//         const friendsData = await response.json();
//         return { friendsData };
//     } catch (error) {
//         console.error("Error fetching data:", error);
//         return { friendsData: [] }; // Return empty array to prevent crashes
//     }
// }