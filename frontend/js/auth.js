import { CONFIG } from "../config.js";
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
    getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

const app = initializeApp(CONFIG.firebase);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

let currentUser = null;
let currentToken = null;

export async function login() {
    console.log("Starting login...");
    await signInWithPopup(auth, provider);
    // token will refresh via listener below
}

export async function logout() {
    await signOut(auth);
}

export function onUserChanged(callback) {
    onAuthStateChanged(auth, async (user) => {
        currentUser = user;
        currentToken = user ? await user.getIdToken() : null;

        console.log("User changed:", user);
        console.log("Token:", currentToken);
        callback(user, currentToken);
    });
}

export function getUser() {
    return currentUser;
}

export async function getToken() {
    if (currentUser) {
        // Optionally refresh token if older than X minutes
        currentToken = await currentUser.getIdToken(/* forceRefresh */ false);
    }
    return currentToken;
}