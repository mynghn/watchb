import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

import {
  axios,
  deleteRefreshTokenCookie,
  updateAvatar,
  deleteAvatar,
  updateBackground,
  deleteBackground,
  updateUser,
} from "../api";
import store, { logout as reduxLogout } from "../store";

import EmailChangeForm from "./EmailChangeForm";
import PasswordChangeForm from "./PasswordChangeForm";
import ImageUpdateModal from "./ImageUpdateModal";
import WarningModal from "./WarningModal";

function ProfilesUpdateModal() {
  const {
    auth: {
      user: { username, profile },
    },
  } = store.getState();

  const [show, setShow] = useState(false);
  const [usernameInput, setUsernameInput] = useState(username);
  const [isUsernameValid, setIsUsernameValid] = useState(false);
  const [isUsernameInvalid, setIsUsernameInvalid] = useState(false);
  const [profileInput, setProfileInput] = useState(profile);

  const handleUsernameChange = (e) => {
    const inputDOM = e.currentTarget;
    setUsernameInput(inputDOM.value);
    if (inputDOM.value === username) {
      setIsUsernameValid(false);
      setIsUsernameInvalid(false);
    } else {
      const isValid = inputDOM.checkValidity();
      setIsUsernameValid(isValid);
      setIsUsernameInvalid(!isValid);
    }
  };
  const handleProfileChange = (e) => {
    setProfileInput(e.currentTarget.value);
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const isValid = form.checkValidity();
    if (isValid) {
      let updateData = {};
      if (usernameInput !== username) updateData["username"] = usernameInput;
      if (profileInput !== profile) updateData["profile"] = profileInput;
      updateUser(updateData).then(() => setShow(false));
    }
  };

  const ACTION_NAME = "프로필 수정";
  const MODAL_TITLE = "프로필 편집";
  const AVATAR_UPDATE_MODAL_PROPS = {
    imgType: "avatar",
    updateFn: updateAvatar,
    deleteFn: deleteAvatar,
    actionNm: "프로필 사진 변경",
    header: "프로필 사진 변경",
  };
  const BACKGROUND_UPDATE_MODAL_PROPS = {
    imgType: "background",
    updateFn: updateBackground,
    deleteFn: deleteBackground,
    actionNm: "배경 사진 변경",
    header: "배경 사진 변경",
  };
  const USERNAME_LABEL = "이름";
  const USERNAME_INPUT_PROPS = {
    type: "text",
    required: true,
    minLength: 2,
    maxLength: 20,
    defaultValue: username,
    onChange: handleUsernameChange,
    isValid: isUsernameValid,
    isInvalid: isUsernameInvalid,
  };
  const USERNAME_INVALID_MESSAGE = "올바르지 않은 이름입니다.";
  const PROFILE_LABEL = "소개";
  const PROFILE_INPUT_PROPS = {
    as: "textarea",
    placeholder: "소개를 입력해주세요.",
    defaultValue: profile,
    onChange: handleProfileChange,
  };

  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        {ACTION_NAME}
      </div>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{MODAL_TITLE}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ImageUpdateModal {...AVATAR_UPDATE_MODAL_PROPS} />
        </Modal.Body>
        <Modal.Body>
          <ImageUpdateModal {...BACKGROUND_UPDATE_MODAL_PROPS} />
        </Modal.Body>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Label>{USERNAME_LABEL}</Form.Label>
              <Form.Control {...USERNAME_INPUT_PROPS} />
              <Form.Control.Feedback
                type="invalid"
                style={{ textAlign: "start" }}
              >
                {USERNAME_INVALID_MESSAGE}
              </Form.Control.Feedback>
            </Form.Group>
            <Form.Group>
              <Form.Label>{PROFILE_LABEL}</Form.Label>
              <Form.Control {...PROFILE_INPUT_PROPS} />
            </Form.Group>
            <Button
              type="submit"
              disabled={usernameInput === username && profileInput === profile}
            >
              확인
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}

function EmailChangeModal() {
  const [show, setShow] = useState(false);
  const showModal = () => setShow(true);
  const hideModal = () => setShow(false);

  const ACTION_NAME = "이메일 변경";
  const MODAL_TITLE = "이메일 변경";

  return (
    <>
      <div onClick={showModal} style={{ cursor: "pointer" }}>
        {ACTION_NAME}
      </div>
      <Modal show={show} onHide={hideModal}>
        <Modal.Header closeButton>
          <Modal.Title>{MODAL_TITLE}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <EmailChangeForm onSuccess={hideModal} />
        </Modal.Body>
      </Modal>
    </>
  );
}

function PasswordChangeModal() {
  const [show, setShow] = useState(false);
  const showModal = () => setShow(true);
  const hideModal = () => setShow(false);

  const ACTION_NAME = "비밀번호 변경";
  const MODAL_TITLE = "비밀번호 변경";

  return (
    <>
      <div onClick={showModal} style={{ cursor: "pointer" }}>
        {ACTION_NAME}
      </div>
      <Modal show={show} onHide={hideModal}>
        <Modal.Header closeButton>
          <Modal.Title>{MODAL_TITLE}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <PasswordChangeForm onSuccess={hideModal} />
        </Modal.Body>
      </Modal>
    </>
  );
}

function VisibilitySettingModal() {
  const {
    auth: {
      user: { visibility: currVisibility },
    },
  } = store.getState();
  const [show, setShow] = useState(false);
  const showModal = () => setShow(true);
  const hideModal = () => setShow(false);

  const [visibility, setVisibility] = useState(currVisibility);

  const handleChange = (e) => {
    const selectedVisibility = e.currentTarget.name;
    setVisibility(selectedVisibility);
    updateUser({ visibility: selectedVisibility });
  };

  const ACTION_NAME = "공개 설정";
  const MODAL_TITLE = "공개 범위";
  const PUBLIC_CHOICE = "public";
  const PUBLIC_LABEL = "전체공개";
  const PUBLIC_TEXT = "\nWatchB의 모든 유저에게 공개합니다.";
  const PRIVATE_CHOICE = "private";
  const PRIVATE_LABEL = "친구공개";
  const PRIVATE_TEXT = "\n내가 팔로우하는 유저에게 공개합니다.";
  const CLOSED_CHOICE = "closed";
  const CLOSED_LABEL = "비공개";
  const CLOSED_TEXT = "\n아무에게도 공개하지 않습니다.";

  return (
    <>
      <div onClick={showModal} style={{ cursor: "pointer" }}>
        {ACTION_NAME}
      </div>
      <Modal show={show} onHide={hideModal}>
        <Modal.Header closeButton>
          <Modal.Title>{MODAL_TITLE}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Check>
              <Form.Check.Input
                type="radio"
                name={PUBLIC_CHOICE}
                checked={visibility === PUBLIC_CHOICE}
                onChange={handleChange}
              />
              <Form.Check.Label>{PUBLIC_LABEL}</Form.Check.Label>
              <Form.Text>{PUBLIC_TEXT}</Form.Text>
            </Form.Check>
            <Form.Check>
              <Form.Check.Input
                type="radio"
                name={PRIVATE_CHOICE}
                checked={visibility === PRIVATE_CHOICE}
                onChange={handleChange}
              />
              <Form.Check.Label>{PRIVATE_LABEL}</Form.Check.Label>
              <Form.Text>{PRIVATE_TEXT}</Form.Text>
            </Form.Check>
            <Form.Check>
              <Form.Check.Input
                type="radio"
                name={CLOSED_CHOICE}
                checked={visibility === CLOSED_CHOICE}
                onChange={handleChange}
              />
              <Form.Check.Label>{CLOSED_LABEL}</Form.Check.Label>
              <Form.Text>{CLOSED_TEXT}</Form.Text>
            </Form.Check>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}

function LogoutModal() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const logout = () => {
    deleteRefreshTokenCookie().then(() => {
      delete axios.defaults.headers.common["Authorization"];
      dispatch(reduxLogout());
      navigate("/");
    });
  };

  return (
    <WarningModal
      callbackFn={logout}
      actionNm="로그아웃"
      warningMsg="로그아웃 하시겠어요?"
      centered
    />
  );
}

export default function UserSettingsModal() {
  const [show, setShow] = useState(false);
  const showModal = () => setShow(true);
  const hideModal = () => setShow(false);

  const ACTION_NAME = "설정";
  const MODAL_TITLE = "설정";

  return (
    <>
      <Button variant="secondary" onClick={showModal}>
        {ACTION_NAME}
      </Button>

      <Modal show={show} onHide={hideModal}>
        <Modal.Header closeButton>
          <Modal.Title>{MODAL_TITLE}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ProfilesUpdateModal />
        </Modal.Body>
        <Modal.Body>
          <EmailChangeModal />
        </Modal.Body>
        <Modal.Body>
          <PasswordChangeModal />
        </Modal.Body>
        <Modal.Body>
          <VisibilitySettingModal />
        </Modal.Body>
        <Modal.Body>
          <LogoutModal />
        </Modal.Body>
      </Modal>
    </>
  );
}
