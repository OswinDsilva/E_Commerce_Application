const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

function buildError(message, response, code) {
  const error = new Error(message)
  error.status = response?.status || 0
  error.code = code || 'REQUEST_FAILED'
  return error
}

function getFriendlyMessage(status, code, fallbackMessage) {
  if (code === 'NETWORK_ERROR') {
    return 'The server is unavailable right now. Please try again shortly.'
  }

  if (code === 'UNAUTHORIZED') {
    return 'Your session has expired. Please sign in again.'
  }

  if (code === 'BAD_REQUEST') {
    return fallbackMessage || 'Please check your input and try again.'
  }

  if (code === 'NOT_FOUND') {
    return 'The requested item could not be found.'
  }

  if (status >= 500 || code === 'SERVER_ERROR') {
    return 'Something went wrong. Please try again.'
  }

  return fallbackMessage || 'Something went wrong. Please try again.'
}

const OPERATION_MESSAGES = {
  authLogin: {
    NETWORK_ERROR: 'Unable to reach the sign-in service right now.',
    UNAUTHORIZED: 'Invalid username or password.',
    BAD_REQUEST: 'Please enter a valid username and password.',
    SERVER_ERROR: 'Sign-in is unavailable right now. Please try again.',
    default: 'Unable to sign in right now.',
  },
  authRegister: {
    NETWORK_ERROR: 'Unable to reach the registration service right now.',
    BAD_REQUEST: 'Please check the registration details and try again.',
    SERVER_ERROR: 'Registration is unavailable right now. Please try again.',
    default: 'Unable to create your account right now.',
  },
  bankAccountsLoad: {
    NETWORK_ERROR: 'Unable to load bank accounts right now.',
    UNAUTHORIZED: 'Your session expired before bank accounts could load.',
    SERVER_ERROR: 'Bank accounts are unavailable right now.',
    default: 'Unable to load bank accounts right now.',
  },
  bankAccountsCreate: {
    NETWORK_ERROR: 'Unable to save that bank account right now.',
    UNAUTHORIZED: 'Your session expired before the account could be saved.',
    BAD_REQUEST: 'Please check the bank account details and try again.',
    SERVER_ERROR: 'Bank account saving is unavailable right now.',
    default: 'Unable to add bank account right now.',
  },
  orderPayment: {
    NETWORK_ERROR: 'Unable to submit payment right now.',
    UNAUTHORIZED: 'Your session expired before payment could be submitted.',
    FORBIDDEN: 'You are not allowed to pay this order.',
    NOT_FOUND: 'This order could not be found.',
    BAD_REQUEST: 'Please check the selected payment details and try again.',
    SERVER_ERROR: 'Payment is unavailable right now.',
    default: 'Unable to process payment right now.',
  },
}

export function getUserFacingErrorMessage(error, operation) {
  const operationMessages = OPERATION_MESSAGES[operation] || {}
  const code = error?.code || 'REQUEST_FAILED'

  if (operationMessages[code]) {
    return operationMessages[code]
  }

  if (code === 'NETWORK_ERROR') {
    return operationMessages.NETWORK_ERROR || 'The server is unavailable right now. Please try again shortly.'
  }

  if (code === 'UNAUTHORIZED') {
    return operationMessages.UNAUTHORIZED || 'Your session has expired. Please sign in again.'
  }

  if (code === 'BAD_REQUEST') {
    return operationMessages.BAD_REQUEST || 'Please check your input and try again.'
  }

  if (code === 'NOT_FOUND') {
    return operationMessages.NOT_FOUND || 'The requested item could not be found.'
  }

  if (code === 'FORBIDDEN') {
    return operationMessages.FORBIDDEN || 'You are not allowed to complete this action.'
  }

  if (error?.status >= 500 || code === 'SERVER_ERROR') {
    return operationMessages.SERVER_ERROR || 'Something went wrong. Please try again.'
  }

  return operationMessages.default || 'Something went wrong. Please try again.'
}

async function readResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }

  const text = await response.text()
  return text ? { message: text } : null
}

export async function apiRequest(path, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      credentials: 'include',
      ...options,
      headers: {
        ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw buildError('Unable to connect to backend', null, 'NETWORK_ERROR')
  }

  const payload = await readResponse(response)

  if (!response.ok) {
    const rawMessage = payload?.error || payload?.message || 'Request failed'
    const code = payload?.code || 'REQUEST_FAILED'
    const message = getFriendlyMessage(response.status, code, rawMessage)
    throw buildError(message, response, code)
  }

  return payload
}

export const isBackendUnavailableError = (error) =>
  error?.code === 'NETWORK_ERROR' || error?.status === 404 || error?.status === 405

export const loginUser = (payload) => apiRequest('/auth/login', {
  method: 'POST',
  body: JSON.stringify(payload),
}).then(response => response.user)

export const registerUser = (payload) => apiRequest('/auth/register', {
  method: 'POST',
  body: JSON.stringify(payload),
}).then(response => response.user)

export const logoutUser = () => apiRequest('/auth/logout', {
  method: 'POST',
})

export const getCurrentUser = () => apiRequest('/auth/me')
  .then(response => response.user)

export const listBankAccounts = () => apiRequest('/bank-accounts')
  .then(response => response.accounts || [])

export const createBankAccount = (payload) => apiRequest('/bank-accounts', {
  method: 'POST',
  body: JSON.stringify(payload),
}).then(response => response.account)

export const deleteBankAccount = (accNo) => apiRequest(`/bank-accounts/${accNo}`, {
  method: 'DELETE',
})

export const payOrder = (orderId, payload) => apiRequest(`/orders/${orderId}/pay`, {
  method: 'POST',
  body: JSON.stringify(payload),
})