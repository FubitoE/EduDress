document.addEventListener('DOMContentLoaded', function () {
    // ログインボタンとポップアップ要素を取得
    const openLoginBtn = document.getElementById("openLoginBtn");
    const loginPopup = document.getElementById("loginPopup");
    const closePopupBtn = document.getElementById("closePopupBtn");
    const form = document.querySelector('form');
    const resultDiv = document.querySelector('.result');
    const radioButtons = document.querySelectorAll('input[name="choice"]');
    const submitButton = document.querySelector('button[type="submit"]');

    // ログインボタンがクリックされたときにポップアップを表示
    if (openLoginBtn) {
        openLoginBtn.addEventListener("click", () => {
            loginPopup.style.display = "flex"; // ポップアップ表示
        });
    }

    // 閉じるボタンがクリックされたときにポップアップを非表示
    if (closePopupBtn) {
        closePopupBtn.addEventListener("click", () => {
            loginPopup.style.display = "none"; // ポップアップ非表示
        });
    }

    // ポップアップ外をクリックしたときに閉じる
    window.addEventListener("click", (event) => {
        if (event.target === loginPopup) {
            loginPopup.style.display = "none"; // ポップアップ外をクリックした場合も閉じる
        }
    });

    // フォームが送信された際の処理
    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // フォームの通常の送信を停止

            // 選択された選択肢を取得
            const selectedChoice = document.querySelector('input[name="choice"]:checked');

            if (selectedChoice) {
                // ラジオボタンを無効化
                radioButtons.forEach((radio) => {
                    radio.disabled = true;
                });

                // 送信ボタンを無効化
                if (submitButton) {
                    submitButton.disabled = true;
                }

                // フォームを送信
                form.submit();
            } else {
                alert('選択肢を選んでください。');
            }
        });
    }

    // 解説が表示された場合にスライドインアニメーションを追加
    if (resultDiv) {
        resultDiv.style.display = 'none'; // 初期状態では非表示
        setTimeout(() => {
            resultDiv.style.display = 'block';
            resultDiv.style.transition = 'all 0.5s ease';
            resultDiv.style.opacity = 1;
        }, 200);
    }
});
