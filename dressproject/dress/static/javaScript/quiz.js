document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.choices-form'); // フォームセレクタを変更
    const resultDiv = document.querySelector('.result');

    // フォームが送信された際の処理
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // フォームの通常の送信を停止

            // 選択された選択肢を取得
            const selectedChoice = document.querySelector('input[name="choice"]:checked');
            
            if (selectedChoice) {
                // フォームデータを送信するための処理
                const formData = new FormData(form);
                
                // ここで非同期でデータを送信する例（Fetch APIを使用）
                fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}', // CSRFトークンをヘッダに追加
                    },
                })
                .then(response => response.json())
                .then(data => {
                    // 送信後の処理（結果表示など）
                    // 必要に応じてHTMLを更新する
                    // 例えば、選択肢や結果の表示を更新する処理をここに追加
                })
                .catch(error => {
                    console.error('Error:', error);
                });
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
