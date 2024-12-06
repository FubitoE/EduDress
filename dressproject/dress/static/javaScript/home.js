document.addEventListener("DOMContentLoaded", () => {
    const nicknameField = document.getElementById("nicknameField");
    const usernameField = document.getElementById("usernameField");
    const popup = document.getElementById("popup");
    const popupInput = document.getElementById("popupInput");
    const cancelButton = document.getElementById("cancelButton");
    let targetField = null;

    nicknameField.addEventListener("click", () => {
        targetField = "nickname";
        popupInput.value = nicknameField.textContent.replace("ニックネーム: ", "");
        popup.classList.remove("hidden");
    });

    usernameField.addEventListener("click", () => {
        targetField = "username";
        popupInput.value = usernameField.textContent.replace("ユーザー名: ", "");
        popup.classList.remove("hidden");
    });

    cancelButton.addEventListener("click", () => {
        popup.classList.add("hidden");
    });

    document.getElementById("popupForm").addEventListener("submit", (e) => {
        e.preventDefault();

        const newValue = popupInput.value;
        const payload = { [targetField]: newValue };

        fetch("/accounts/update-user-info/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCsrfToken(),
            },
            body: JSON.stringify(payload),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    if (targetField === "nickname") {
                        nicknameField.textContent = `ニックネーム: ${newValue}`;
                    } else if (targetField === "username") {
                        usernameField.textContent = `ユーザー名: ${newValue}`;
                    }
                    alert(data.message);
                } else {
                    alert(data.message);
                }
                popup.classList.add("hidden");
            })
            .catch((error) => {
                console.error("エラー:", error);
                alert("エラーが発生しました。再試行してください。");
            });
    });

    function getCsrfToken() {
        return document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1] || "";
    }
});
