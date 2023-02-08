module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/eslint-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    project: 'tsconfig.eslint.json',
    ecmaVersion: 2020,
    sourceType: 'module',
    extraFileExtensions: ['.svelte'],
  },
  env: {
    es2017: true,
    browser: true,
  },
  plugins: ['@typescript-eslint', 'svelte3'],
  overrides: [{ files: ['*.svelte'], processor: 'svelte3/svelte3' }],
  rules: {
    '@typescript-eslint/no-unused-vars': ['warn', { args: 'none' }],
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-namespace': 'off',
    '@typescript-eslint/no-use-before-define': 'off',
    '@typescript-eslint/quotes': [
      'error',
      'single',
      { avoidEscape: true, allowTemplateLiterals: false },
    ],
    curly: ['error', 'all'],
    eqeqeq: 'error',
    'prefer-arrow-callback': 'error',
  },
  settings: {
    'svelte3/typescript': true,
  },
};
