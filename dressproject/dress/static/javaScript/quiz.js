document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const resultDiv = document.querySelector('.result');
    const toggleResultBtn = document.querySelector('.toggle-result-btn');

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // デフォルト送信を無効化

            const selectedChoice = document.querySelector('input[name="choice"]:checked');
            if (selectedChoice) {
                // サーバー送信の代わりに結果を表示
                resultDiv.style.display = 'block';
                toggleResultBtn.style.display = 'inline-block'; // 解説ボタンを表示
            } else {
                alert('選択肢を選んでください。');
            }
        });
    }

    // 解説を開閉する機能
    if (toggleResultBtn) {
        toggleResultBtn.addEventListener('click', function () {
            if (resultDiv.style.display === 'block') {
                resultDiv.style.display = 'none';
                toggleResultBtn.textContent = '解説を見る';
            } else {
                resultDiv.style.display = 'block';
                toggleResultBtn.textContent = '解説を閉じる';
            }
        });
    }
});
