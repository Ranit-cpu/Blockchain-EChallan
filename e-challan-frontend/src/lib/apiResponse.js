export function unwrapData(res) {
    const body = res?.data ?? res;
    return body?.data ?? body;
  }
  
  export function unwrapPaginated(res) {
    return res?.data ?? res;
  }