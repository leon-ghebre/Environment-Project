import js from "@eslint/js";

export default [
  js.configs.recommended,
  {
    files: ["assets/static/js/**/*.js"],

    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        document: "readonly",
        window: "readonly",
        console: "readonly",
        fetch: "readonly",
        URLSearchParams: "readonly",
        URL: "readonly",
        alert: "readonly",
        setInterval: "readonly",
        localStorage: "readonly",
        Plotly: "readonly",
        onDaysChange: "readonly",
        doExport: "readonly"
      }
    },

    rules: {
      "no-unused-vars": "warn",
      "no-console": "off",
      "semi": ["error", "always"],
      "curly": "error"
    }
  }
];