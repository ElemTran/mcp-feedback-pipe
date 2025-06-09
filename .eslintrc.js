module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    'jest/globals': true
  },
  extends: [
    'eslint:recommended',
    'standard',
    'plugin:jest/recommended',
    'prettier'
  ],
  plugins: [
    'jest'
  ],
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module'
  },
  rules: {
    // Console statements - allow in development, warn in production
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',

    // Function complexity and length
    'max-lines-per-function': ['warn', { max: 80, skipBlankLines: true, skipComments: true }],
    complexity: ['warn', { max: 10 }],

    // Code style
    'max-len': ['error', {
      code: 100,
      ignoreUrls: true,
      ignoreStrings: true,
      ignoreTemplateLiterals: true,
      ignorePattern: '^\\s*// .*$|updateCountdownDisplay.*|innerHTML.*=.*$'
    }],
    indent: ['error', 2],
    quotes: ['error', 'single'],
    'comma-dangle': ['error', 'never'],
    'no-trailing-spaces': 'error',
    'eol-last': 'error',
    'padded-blocks': ['error', 'never'],
    'object-shorthand': 'warn',
    'quote-props': ['error', 'as-needed'],
    'no-multi-spaces': 'error',

    // Global variables for browser environment
    'no-undef': 'error'
  },
  globals: {
    // Browser globals that might not be recognized
    mermaid: 'readonly',
    marked: 'readonly',
    Prism: 'readonly'
  },
  overrides: [
    {
      // Jest test files
      files: ['tests/**/*.js', '**/*.test.js', '**/*.spec.js'],
      env: {
        'jest/globals': true
      },
      rules: {
        // Relax some rules for test files
        'max-lines-per-function': 'off',
        'no-console': 'off'
      }
    }
  ]
}
