import runtimeEnv from '@mars/heroku-js-runtime-env';

const env = runtimeEnv();
const apiBasePath = (env.REACT_APP_API_BASE_PATH || 'http://localhost:8001').replace(/\/$/, '');

const config = {
  apiBasePath,
  reactAppMode: process.env.REACT_APP_MODE || 'dev',
};

export default config;
