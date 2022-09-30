import { emailAlreadyRegistered, INVALID_EMAIL_PATTERN_MESSAGE } from "../api";

export const checkEmailPatternAndRedundancy = async (email) => {
  let isValid = true;
  let message;
  try {
    if (await emailAlreadyRegistered(email)) {
      isValid = false;
      message = "이미 가입된 이메일입니다.";
    }
  } catch (error) {
    const {
      response: {
        data: { email: errorMessages },
      },
    } = error;
    if (
      errorMessages &&
      Array.isArray(errorMessages) &&
      errorMessages.includes(INVALID_EMAIL_PATTERN_MESSAGE)
    ) {
      isValid = false;
    }
  }
  return { isValid, message };
};

export const checkPasswordPattern = (password) => {
  const en = /[a-z]/i;
  const num = /\d/;
  const spcialChar = /[^a-z\d]/i;
  const isValid =
    en.test(password) + num.test(password) + spcialChar.test(password) >= 2;
  return {
    isValid,
    message: isValid
      ? ""
      : "비밀번호는 영문, 숫자, 특수문자 중 2가지 이상을 조합해야 합니다.",
  };
};
