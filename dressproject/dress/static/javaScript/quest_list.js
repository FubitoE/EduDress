document.addEventListener('DOMContentLoaded', function () {
    const questionContainer = document.querySelector('.button-container');

    // APIリクエスト
    fetch('/api/questions/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.length === 0) {
                questionContainer.innerHTML = `
                    <div class="empty-message">
                        <p>この難易度の問題はまだ登録されていません。</p>
                        <a href="/exam_year_list/" class="btn btn-back">他の年度を選択する</a>
                    </div>
                `;
            } else {
                questionContainer.innerHTML = data.map(question => `
                    <a href="/questions/${question.questions_id}/" class="btn btn-custom">
                        問題 ${question.questions_number}: ${question.questions_text}
                    </a>
                `).join('');
            }
        })
        .catch(error => {
            console.error('Error fetching questions:', error);
            questionContainer.innerHTML = `<p>問題を読み込む際にエラーが発生しました。</p>`;
        });
});
