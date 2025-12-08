/**
 * Ant Design Vue 主题配置
 * 用于 ConfigProvider 组件的 theme 属性
 */

export const themeConfig = {
    token: {
        // 主色调
        colorPrimary: '#016179',
        colorLink: '#016179',
        colorLinkHover: '#0188a6',

        // 圆角
        borderRadius: 6,
        borderRadiusLG: 8,
        borderRadiusSM: 4,

        // 字体
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'",
        fontSize: 14,

        // 其他配置
        colorBgContainer: '#ffffff',
        colorBgLayout: '#f5f5f5',
        colorBorder: '#d9d9d9',
        colorBorderSecondary: '#f0f0f0',
    },
    components: {
        Button: {
            borderRadius: 6,
        },
        Input: {
            borderRadius: 6,
        },
        Select: {
            borderRadius: 6,
        },
        Card: {
            borderRadius: 8,
        },
        Modal: {
            borderRadius: 8,
        },
        Table: {
            borderRadius: 8,
        },
        Menu: {
            itemBorderRadius: 6,
        },
    },
};

export default themeConfig;
