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
      console.log(isValid);
      setIsUsernameValid(isValid);
      setIsUsernameInvalid(!isValid);
    }
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

  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        프로필 수정
      </div>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>프로필 편집</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ImageUpdateModal
            imgType="avatar"
            updateFn={updateAvatar}
            deleteFn={deleteAvatar}
            actionNm="프로필 사진 변경"
            header="프로필 사진 변경"
          />
        </Modal.Body>
        <Modal.Body>
          <ImageUpdateModal
            imgType="background"
            updateFn={updateBackground}
            deleteFn={deleteBackground}
            actionNm="배경 사진 변경"
            header="배경 사진 변경"
          />
        </Modal.Body>
        <Modal.Body>
          <Form validated={false} onSubmit={handleSubmit}>
            <Form.Group>
              <Form.Label>이름</Form.Label>
              <Form.Control
                type="text"
                required
                minLength={2}
                maxLength={20}
                defaultValue={username}
                onChange={handleUsernameChange}
                isValid={isUsernameValid}
                isInvalid={isUsernameInvalid}
              />
              <Form.Control.Feedback
                type="invalid"
                style={{ textAlign: "start" }}
              >
                올바르지 않은 이름입니다.
              </Form.Control.Feedback>
            </Form.Group>
            <Form.Group>
              <Form.Label>소개</Form.Label>
              <Form.Control
                as="textarea"
                placeholder="소개를 입력해주세요."
                defaultValue={profile}
                onChange={(e) => {
                  setProfileInput(e.currentTarget.value);
                }}
              />
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

  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        이메일 변경
      </div>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>이메일 변경</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <EmailChangeForm onSuccess={() => setShow(false)} />
        </Modal.Body>
      </Modal>
    </>
  );
}

function PasswordChangeModal() {
  const [show, setShow] = useState(false);

  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        비밀번호 변경
      </div>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>비밀번호 변경</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <PasswordChangeForm onSuccess={() => setShow(false)} />
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
  const [visibility, setVisibility] = useState(currVisibility);

  const handleChange = (e) => {
    const selectedVisibility = e.currentTarget.name;
    setVisibility(selectedVisibility);
    updateUser({ visibility: selectedVisibility });
  };

  return (
    <>
      <div onClick={() => setShow(true)} style={{ cursor: "pointer" }}>
        공개 설정
      </div>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>공개 범위</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={() => console.log("dqwer")}>
            <Form.Check>
              <Form.Check.Input
                type="radio"
                name="public"
                checked={visibility === "public"}
                onChange={handleChange}
              />
              <Form.Check.Label>전체공개</Form.Check.Label>
              <Form.Text> WatchB의 모든 유저에게 공개합니다.</Form.Text>
            </Form.Check>
            <Form.Check type="radio">
              <Form.Check.Input
                type="radio"
                name="private"
                checked={visibility === "private"}
                onChange={handleChange}
              />
              <Form.Check.Label>친구공개</Form.Check.Label>
              <Form.Text> 내가 팔로우하는 유저에게 공개합니다.</Form.Text>
            </Form.Check>
            <Form.Check type="radio">
              <Form.Check.Input
                type="radio"
                name="closed"
                checked={visibility === "closed"}
                onChange={handleChange}
              />
              <Form.Check.Label>비공개</Form.Check.Label>
              <Form.Text> 아무에게도 공개하지 않습니다.</Form.Text>
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

  return (
    <WarningModal
      callbackFn={() => {
        deleteRefreshTokenCookie().then(() => {
          delete axios.defaults.headers.common["Authorization"];
          dispatch(reduxLogout());
          navigate("/");
        });
      }}
      actionNm="로그아웃"
      warningMsg="로그아웃 하시겠어요?"
      centered
    />
  );
}

export default function UserSettingsModal() {
  const [show, setShow] = useState(false);

  return (
    <>
      <Button variant="secondary" onClick={() => setShow(true)}>
        설정
      </Button>

      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>설정</Modal.Title>
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
