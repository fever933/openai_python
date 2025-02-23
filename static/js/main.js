document.addEventListener('DOMContentLoaded', function () {
    // 初始化日期选择器
    flatpickr("#datePicker", {
        locale: "zh",
        dateFormat: "Y-m-d",
        defaultDate: new Date(new Date().setDate(new Date().getDate() + 7))
    });

    // 初始化创建日期选择器
    flatpickr("#createDatePicker", {
        locale: "zh",
        dateFormat: "Y-m-d",
        defaultDate: new Date()
    });

    // 加载食物列表
    refreshList();

    // 添加食物表单提交
    document.getElementById('addFoodForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        fetch('/api/foods', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                alert('添加成功！');
                e.target.reset();
                // 重新设置表单的默认值
                flatpickr("#datePicker", {
                    locale: "zh",
                    dateFormat: "Y-m-d",
                    defaultDate: new Date(new Date().setDate(new Date().getDate() + 7))
                });
                flatpickr("#createDatePicker", {
                    locale: "zh",
                    dateFormat: "Y-m-d",
                    defaultDate: new Date()
                });
                refreshList();
            })
            .catch(error => alert('添加失败：' + error));
    });

    // 搜索功能
    document.getElementById('searchInput').addEventListener('input', function (e) {
        const searchTerm = e.target.value.toLowerCase();
        const rows = document.querySelectorAll('#foodList tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });

    // 添加食材建议表单提交
    document.getElementById('suggestionForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const suggestionsList = document.getElementById('suggestionsList');
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        // Show loading state
        suggestionsList.innerHTML = '<div class="loading">正在生成建议...</div>';

        try {
            const response = await fetch('/api/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)

            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Safely parse and render markdown
                try {
                    suggestionsList.innerHTML = marked.parse(buffer);
                } catch (parseError) {
                    console.warn('Markdown parse error:', parseError);
                }
            }

            // Final decode
            buffer += decoder.decode();
            suggestionsList.innerHTML = marked.parse(buffer);

        } catch (error) {
            console.error('Error:', error);
            suggestionsList.innerHTML = `<div class="error">获取建议时出错: ${error.message}</div>`;
        }
    });
});

function refreshList() {
    fetch('/api/foods')
        .then(response => response.json())
        .then(foods => {
            const tbody = document.getElementById('foodList');
            tbody.innerHTML = '';

            if (foods.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8">没有食物数据</td></tr>';
                return;
            }

            foods.forEach(food => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${food.name || ''}</td>
                    <td>${food.quantity || ''}${food.unit || ''}</td>
                    
                    <td>${food.category || ''}</td>
                    <td>${food.create_date || ''}</td>
                    <td>${food.expiry_date || ''}</td>
                    <td class="status-${getStatusClass(food.status || '')}">${food.status || ''}</td>
                    <td>
                        <button class="btn btn-danger btn-remove" 
                                onclick="removeFood('${food.id}', '${food.name}')">
                            删除
                        </button> / 
                        <button class="btn btn-danger btn-remove" 
                                onclick="clearFood('${food.id}', '${food.name}')">
                            清空
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            const tbody = document.getElementById('foodList');
            tbody.innerHTML = `<tr><td colspan="8">加载数据时出错: ${error.message}</td></tr>`;
        });
}

function removeFood(id, name) {
    const quantity = prompt(`要移除多少个/份 ${name}？`, "1");
    if (quantity === null) return;

    fetch(`/api/foods/${id}?quantity=${quantity}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            alert('删除成功！');
            refreshList();
        })
        .catch(error => alert('删除失败：' + error));
}

function clearFood(id, name) {
    if (!confirm(`确定要移除所有${name}吗？`)) return;

    fetch(`/api/foods/all/${id}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            alert(`所有${name}已删除！`);
            refreshList();
        })
        .catch(error => alert(`删除所有${name}失败：` + error));
}

function checkExpired() {
    const today = new Date();
    fetch('/api/foods')
        .then(response => response.json())
        .then(foods => {
            const expired = foods.filter(food =>
                new Date(food.expiry_date) < today
            );

            if (expired.length > 0) {
                const message = expired.map(food =>
                    `${food.name} - 过期日期: ${food.expiry_date}`
                ).join('\n');
                alert('以下食物已过期：\n\n' + message);
            } else {
                alert('没有过期食物！');
            }
        });
}

function getStatusClass(status) {
    switch (status) {
        case '已过期': return 'expired';
        case '即将过期': return 'warning';
        default: return 'normal';
    }
} 