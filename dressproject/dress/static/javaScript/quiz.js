document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const resultDiv = document.querySelector('.result');

    // フォームが送信された際の処理
    if (form) {
        form.addEventListener('submit', function(event) {
            event.preventDefault(); // フォームの通常の送信を停止

            // 選択された選択肢を取得
            const selectedChoice = document.querySelector('input[name="choice"]:checked');
            
            if (selectedChoice) {
                form.submit(); // 選択肢が選ばれていたらフォームを送信
            } else {
                alert('選択肢を選んでください。');
            }
        });
    }

    // 解説が表示された場合にスライドインアニメーションを追加
    if (resultDiv) {
        resultDiv.style.opacity = 0; // 初期状態で透明
        resultDiv.style.transition = 'opacity 0.5s ease';

        setTimeout(() => {
            resultDiv.style.opacity = 1;
        }, 200);
    }
});
