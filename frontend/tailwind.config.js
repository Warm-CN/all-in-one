/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // 主色调：深邃的科技蓝
                primary: {
                    50: '#eff6ff',
                    100: '#dbeafe',
                    200: '#bfdbfe',
                    300: '#93c5fd',
                    400: '#60a5fa',
                    500: '#2563eb',  // 主色调
                    600: '#1d4ed8',
                    700: '#1e40af',
                    800: '#1e3a8a',
                    900: '#1e3a8a',
                    950: '#172554',
                },
            },
            borderRadius: {
                // 统一大圆角规范
                'card': '16px',
                'button': '12px',
            },
            backdropBlur: {
                'glass': '12px',
            },
            backgroundColor: {
                // 毛玻璃背景
                'glass': 'rgba(255, 255, 255, 0.7)',
                'glass-dark': 'rgba(255, 255, 255, 0.1)',
            },
            borderColor: {
                'glass': 'rgba(255, 255, 255, 0.3)',
            },
            boxShadow: {
                // 轻盈的柔和投影
                'soft': '0 2px 8px rgba(0, 0, 0, 0.08)',
                'soft-lg': '0 4px 16px rgba(0, 0, 0, 0.1)',
                'soft-xl': '0 8px 24px rgba(0, 0, 0, 0.12)',
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
            },
            backgroundImage: {
                // 淡雅的冷色调渐变
                'gradient-main': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'gradient-cool': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                'gradient-sky': 'linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 50%, #80deea 100%)',
                'gradient-blue': 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%)',
            },
            animation: {
                // 预留动画配置（配合 animate.css 和 GSAP）
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'scale-in': 'scaleIn 0.3s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                scaleIn: {
                    '0%': { transform: 'scale(0.9)', opacity: '0' },
                    '100%': { transform: 'scale(1)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
}
