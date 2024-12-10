document.addEventListener('DOMContentLoaded', () => {
    const questionArea = document.getElementById('question-area');
    const choicesArea = document.getElementById('choices-area');
    const resultArea = document.getElementById('result-area');
    const resultMessage = document.getElementById('result-message');
    const nextQuestionButton = document.getElementById('next-question');
    const quizForm = document.getElementById('quiz-form');

    let currentQuestionId = null;

    // 問題をAPIから取得
    async function fetchQuestion() {
        try {
            const response = await fetch('/api/question/');
            if (!response.ok) {
                throw new Error('問題の取得に失敗しました。');
            }

            const data = await response.json();
            displayQuestion(data);
        } catch (error) {
            alert(error.message);
        }
    }

    // 問題を表示
    function displayQuestion(data) {
        questionArea.querySelector('#question-title').textContent = `問題: ${data.questions_number}`;
        questionArea.querySelector('#question-text').textContent = data.questions_text;

        // 選択肢をクリアして新しい選択肢を追加
        choicesArea.innerHTML = '';
        for (const [key, value] of Object.entries(data.choices)) {
            const choice = document.createElement('label');
            choice.innerHTML = `
                <input type="radio" name="choice" value="${key}">
                ${key.toUpperCase()}: ${value}
            `;
            choicesArea.appendChild(choice);
            choicesArea.appendChild(document.createElement('br'));
        }

        currentQuestionId = data.question_id;
        resultArea.style.display = 'none';
        quizForm.style.display = 'block';
    }

    // ユーザーの回答を送信
    quizForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(quizForm);
        const selectedChoice = formData.get('choice');

        if (!selectedChoice) {
            alert('選択肢を選んでください！');
            return;
        }

        try {
            const response = await fetch(`/questions/${currentQuestionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
                body: JSON.stringify({ choice: selectedChoice }),
            });

            const data = await response.json();

            // 結果を表示
            quizForm.style.display = 'none';
            resultArea.style.display = 'block';
            if (data.correct) {
                resultMessage.textContent = '正解です！';
                resultMessage.style.color = 'green';
            } else {
                resultMessage.textContent = '不正解です！';
                resultMessage.style.color = 'red';
            }
        } catch (error) {
            alert('回答の送信に失敗しました。');
        }
    });

    // 次の問題を取得
    nextQuestionButton.addEventListener('click', fetchQuestion);

    // 初回ロード時に問題を取得
    fetchQuestion();
});
