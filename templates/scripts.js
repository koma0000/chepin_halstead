function calculateMetrics() {
    const description = document.getElementById('description').value;
    const code = document.getElementById('code').value;

    fetch('http://localhost:5000/calculate_halstead', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({description, code}),
    })
        .then(response => response.json())
        .then(result => {
            displayResult(result);
            getAllPrograms();
        })
        .catch(error => console.error('Ошибка:', error));
}

function displayResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = ``;
}

function getAllPrograms() {
    fetch('http://localhost:5000/all_programs')
        .then(response => response.json())
        .then(programs => {
            const programsList = document.getElementById('programsList');
            programsList.innerHTML = '';

            programs.forEach(program => {
                programsList.innerHTML += `
<h3><hr></h3>
                           <h3>     Номер программы: ${program.program_id}, Описание: ${program.program_des} <button onclick="deleteProgram(${program.program_id})" class="delete">Удалить</button>  <br>
Параметр Чепина Q: ${program.chepin_Q}

</h3>

                                P: <input type="number" id="P_${program.program_id}" step="any" value="${program.chepin_P || ''}">
                                M: <input type="number" id="M_${program.program_id}" step="any" value="${program.chepin_M || ''}">
                                C: <input type="number" id="C_${program.program_id}" step="any" value="${program.chepin_C || ''}">
                                T: <input type="number" id="T_${program.program_id}" step="any" value="${program.chepin_T || ''}">
                                <button onclick="calculateChepin(${program.program_id})">Рассчитать метрику Чепина</button>
<h3>
                                Холстед:
</h3>

                                    <li>Общее количество операторов : ${program.halstead_total_operators}
                                    <li>Общее количество операндов : ${program.halstead_total_operands}
                                    <li>Уникальные операторы : ${program.halstead_unique_operators}
                                    <li>Уникальные операнды : ${program.halstead_unique_operands}
                                    <li>Длина программы : ${program.halstead_program_length}
                                    <li>Словарь : ${program.halstead_vocabulary}
                                    <li>Объем программы : ${program.halstead_program_volume}
                                    <li>Сложность программы : ${program.halstead_program_difficulty}
                                    <li>Затраты на написание программы : ${program.halstead_program_effort}
                                    <li>Время написания программы : ${program.halstead_programming_time}
                                    <li>Ошибки программирования : ${program.halstead_programming_errors}
                                    `;
            });
        })
        .catch(error => console.error('Ошибка:', error));
}

function deleteProgram(programId) {
    fetch(`http://localhost:5000/delete_program/${programId}`, {
        method: 'DELETE',
    })
        .then(response => {
            if (response.ok) {
                getAllPrograms();
            } else {
                console.error('Не удалось удалить программу');
            }
        })
        .catch(error => console.error('Ошибка:', error));
}

function calculateChepin(programId) {
    const P = document.getElementById(`P_${programId}`).value;
    const M = document.getElementById(`M_${programId}`).value;
    const C = document.getElementById(`C_${programId}`).value;
    const T = document.getElementById(`T_${programId}`).value;

    const data = {
        P: parseFloat(P),
        M: parseFloat(M),
        C: parseFloat(C),
        T: parseFloat(T)
    };

    fetch(`http://localhost:5000/calculate_chepin/${programId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            displayResult(result);
            getAllPrograms();
        })
        .catch(error => console.error('Ошибка при расчете метрики Чепина:', error));
}

getAllPrograms();
