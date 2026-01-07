/**
 * 数据导出工具类
 * 支持CSV和HTML格式导出
 */
class DataExporter {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8004';
    }

    /**
     * 导出数据
     * @param {string} dataType - 数据类型 (sales, competitors, customers, inventory, medical)
     * @param {string} format - 导出格式 (csv, html)
     * @param {object} filters - 筛选条件 (可选)
     */
    async exportData(dataType, format = 'csv', filters = {}) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/export/data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    data_type: dataType,
                    format: format,
                    filters: filters
                })
            });

            if (!response.ok) {
                throw new Error('导出失败');
            }

            // 下载文件
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // 从响应头获取文件名
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `${dataType}_export.csv`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            return { success: true, filename: filename };
        } catch (error) {
            console.error('导出失败:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * 获取可导出的数据类型列表
     */
    async getDataTypes() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/export/data-types`);
            const data = await response.json();
            return data.data_types;
        } catch (error) {
            console.error('获取数据类型失败:', error);
            return [];
        }
    }

    /**
     * 前端直接导出为CSV (无需后端)
     * @param {array} data - 数据数组
     * @param {array} columns - 列名数组
     * @param {string} filename - 文件名
     */
    exportToCSV(data, columns, filename = 'export.csv') {
        // 创建CSV内容
        let csvContent = columns.join(',') + '\n';

        data.forEach(row => {
            const values = columns.map(col => {
                const value = row[col] || '';
                // 处理包含逗号的值
                return String(value).includes(',') ? `"${value}"` : value;
            });
            csvContent += values.join(',') + '\n';
        });

        // 添加BOM以支持中文
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });

        // 下载文件
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    /**
     * 前端直接导出为JSON
     * @param {object} data - 数据对象
     * @param {string} filename - 文件名
     */
    exportToJSON(data, filename = 'export.json') {
        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    /**
     * 导出当前页面数据
     * @param {string} pageType - 页面类型
     * @param {array} tableData - 表格数据
     * @param {array} columns - 列名
     */
    exportPageData(pageType, tableData, columns) {
        const timestamp = new Date().toISOString().slice(0, 10);
        const filename = `${pageType}_${timestamp}.csv`;

        this.exportToCSV(tableData, columns, filename);
    }
}

// 创建全局实例
const exporter = new DataExporter();

// Vue指令示例
// 在Vue组件中使用:
// <button v-export="'csv'" @click="exportData">导出CSV</button>
const exportDirective = {
    mounted(el, binding) {
        el.addEventListener('click', () => {
            const format = binding.value || 'csv';
            console.log(`导出格式: ${format}`);
        });
    }
};

// 如果在Vue环境中,自动注册指令
if (typeof Vue !== 'undefined') {
    Vue.directive('export', exportDirective);
}
