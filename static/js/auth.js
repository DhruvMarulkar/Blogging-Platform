let currentUser = null;
let fetchPromise = null;

export async function getCurrentUser() {
    if (currentUser) {
        return currentUser;
    }


    if (fetchPromise) {
        return fetchPromise;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
        return null;
    }

    fetchPromise = (async () => {
        try {
            const response = await fetch("/api/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                currentUser = await response.json();
                return currentUser;
            }

            localStorage.removeItem("access_token");
            return null;
        } catch (error) {
            console.error("Error fetching current user:", error);
            return null;
        } finally {
            fetchPromise = null;
        }
    })();

    return fetchPromise;
}

export function logout() {
    localStorage.removeItem("access_token");
    currentUser = null;
    window.location.href = "/";
}

export function getToken() {
    return localStorage.getItem("access_token");
}

export function setToken(token) {
    localStorage.setItem("access_token", token);
}

export function clearUserCache() {
    currentUser = null;
}