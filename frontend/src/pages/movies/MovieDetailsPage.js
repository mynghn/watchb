import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import Image from "react-bootstrap/Image";
import Figure from "react-bootstrap/Figure";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Button from "react-bootstrap/Button";
import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";
import Card from "react-bootstrap/Card";
import Carousel from "react-bootstrap/Carousel";

import { retrieveMovie } from "../../api";
import RatingStars from "../../components/RatingStars";
import { useDispatch, useSelector } from "react-redux";
import { detachMovie } from "../../store";

const EMPTY_POSTER_IMG =
  "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4Ij4KICAgIDxnIGZpbGw9Im5vbmUiIGZpbGwtcnVsZT0iZXZlbm9kZCI+CiAgICAgICAgPHBhdGggZmlsbD0iI0Q0RDRENCIgZD0iTTQyIDQxLjI1aC01LjM4MnYtNy41NjZoNi42MzJWNDBjMCAuNjg5LS41NjEgMS4yNS0xLjI1IDEuMjV6TTQuNzUgNDB2LTYuMzE2aDYuNjMydjcuNTY2SDZjLS42ODkgMC0xLjI1LS41NjEtMS4yNS0xLjI1ek02IDYuNzVoNS4zODJ2Ny41NjZINC43NVY4YzAtLjY4OS41NjEtMS4yNSAxLjI1LTEuMjV6TTQzLjI1IDh2Ni4zMTZoLTYuNjMyVjYuNzVINDJjLjY4OSAwIDEuMjUuNTYxIDEuMjUgMS4yNXptLTYuNjMyIDI0LjE4NGg2LjYzMlYyNC43NWgtNi42MzJ2Ny40MzR6TTEyLjg4MiA0MS4yNWgyMi4yMzZ2LTE2LjVIMTIuODgydjE2LjV6TTQuNzUgMzIuMTg0aDYuNjMyVjI0Ljc1SDQuNzV2Ny40MzR6bTAtOC45MzRoNi42MzJ2LTcuNDM0SDQuNzV2Ny40MzR6bTguMTMyIDBoMjIuMjM2VjYuNzVIMTIuODgydjE2LjV6bTIzLjczNiAwaDYuNjMydi03LjQzNGgtNi42MzJ2Ny40MzR6TTQyIDUuMjVINkEyLjc1MiAyLjc1MiAwIDAgMCAzLjI1IDh2MzJBMi43NTIgMi43NTIgMCAwIDAgNiA0Mi43NWgzNkEyLjc1MiAyLjc1MiAwIDAgMCA0NC43NSA0MFY4QTIuNzUyIDIuNzUyIDAgMCAwIDQyIDUuMjV6Ii8+CiAgICA8L2c+Cjwvc3ZnPgo=";

function CreditCard({
  job,
  cameo_type: cameoType,
  role_name: roleName,
  person,
  ...props
}) {
  const [personState, setPersonState] = useState(person);
  useEffect(() => {
    setPersonState(person);
  }, [person]);
  return (
    <Carousel.Item {...props}>
      <img
        src={personState.avatar_url}
        alt={personState.name}
        style={{ width: "30%", heigh: "30%" }}
      />
      <Carousel.Caption>
        <h5>{personState.name}</h5>
        <p>{job}</p>
      </Carousel.Caption>
    </Carousel.Item>
  );
}

function CreditsCarousel({ directors = [], cast = [] }) {
  return (
    <Carousel>
      {directors.concat(cast).map((credit, idx) => (
        <CreditCard key={idx} {...credit} />
      ))}
    </Carousel>
  );
}

function MovieDetailsCard() {
  const {
    original_title: originalTitle,
    production_year: prodYear,
    genres,
    countries,
    running_time: runningTime,
    film_rating: filmRating,
    synopsys,
    credits,
  } = useSelector((state) => state.movies.movie);

  const navigate = useNavigate();
  const { pathname } = useLocation();

  const [mainGenre, setMainGenre] = useState("");
  useEffect(() => {
    if (genres) {
      setMainGenre(genres[0].name);
    }
  }, [genres]);

  const [mainCountry, setMainCountry] = useState("");
  useEffect(() => {
    if (countries) {
      setMainCountry(countries[0].name);
    }
  }, [countries]);

  const [directors, setDirectors] = useState([]);
  const [cast, setCast] = useState([]);
  useEffect(() => {
    if (credits) {
      setDirectors(credits.filter(({ job }) => job === "director"));
      setCast(credits.filter(({ job }) => job === "actor"));
    }
  }, [credits]);

  return (
    <Card>
      <Card.Body>
        <h4>내가 좋아할 이유</h4>
      </Card.Body>
      <Card.Body>
        <h4>기본 정보</h4>
        <div
          onClick={() => navigate(`${pathname}/overview`)}
          style={{ cursor: "pointer" }}
        >
          더보기
        </div>
      </Card.Body>
      <Card.Body>
        {originalTitle}
        <br />
        {`${prodYear} ・ ${mainGenre} ・ ${mainCountry}`}
        <br />
        {`${runningTime} ・ ${filmRating}`}
      </Card.Body>
      <Card.Body>{synopsys}</Card.Body>
      <Card.Body>
        <h4>출연/제작</h4>
        <CreditsCarousel directors={directors} cast={cast} />
      </Card.Body>
      <Card.Body>
        <h4>별점 그래프</h4>
      </Card.Body>
      <Card.Body>
        <h4>본 친구</h4>
      </Card.Body>
      <Card.Body>
        <h4>코멘트</h4>
        <div
          onClick={() => navigate(`${pathname}/reviews`)}
          style={{ cursor: "pointer" }}
        >
          더보기
        </div>
      </Card.Body>
      <Card.Body>Carousel with Tab</Card.Body>
      <Card.Body>
        <h4>갤러리</h4>
      </Card.Body>
      <Card.Body>
        <h4>동영상</h4>
      </Card.Body>
      <Card.Body>
        <h4>이 작품이 담긴 컬렉션</h4>
      </Card.Body>
      <Card.Body>
        <h4>비슷한 작품</h4>
      </Card.Body>
    </Card>
  );
}

function MyReviewCard() {
  return (
    <Card>
      <div>my avatar</div>
      <div>my review</div>
      <div>삭제</div>
      <div>수정</div>
    </Card>
  );
}

function Header() {
  const {
    title,
    production_year: prodYear,
    poster_set: posterSet,
    genres,
    countries,
  } = useSelector((state) => state.movies.movie);

  const [posterURL, setPosterURL] = useState(EMPTY_POSTER_IMG);
  const [genresStr, setGenresStr] = useState("");
  const [countriesStr, setCountriesStr] = useState("");

  useEffect(() => {
    // poster
    if (posterSet) {
      const [{ image_url }] = posterSet.filter(({ is_main }) => is_main);
      setPosterURL(image_url);
    }
  }, [posterSet]);

  useEffect(() => {
    // genres
    if (genres) {
      setGenresStr(genres.map(({ name }) => name).join("/"));
    }
  }, [genres]);

  useEffect(() => {
    // countries
    if (countries) {
      setCountriesStr(countries.map(({ name }) => name).join("/"));
    }
  }, [countries]);

  return (
    <div>
      <Figure>
        <Figure.Image width={149} height={217} src={posterURL} />
      </Figure>
      <h1>{title}</h1>
      <div>{`${prodYear} ・ ${genresStr} ・ ${countriesStr}`}</div>
      <div>
        <em>예상 ★4.0</em>
        {"    평균 ★4.3 (25만명)"}
      </div>
      <div>
        <RatingStars />
        <ButtonGroup>
          <Button>보고싶어요</Button>
          <Button>코멘트</Button>
          <DropdownButton as={ButtonGroup} title="더보기">
            <Dropdown.Item eventKey="1">관심없어요</Dropdown.Item>
          </DropdownButton>
        </ButtonGroup>
      </div>
    </div>
  );
}

function Wallpaper() {
  const { still_set: stillSet, poster_set: posterSet } = useSelector(
    (state) => state.movies.movie
  );
  const [wallpaperURL, setWallpaperURL] = useState(EMPTY_POSTER_IMG);
  useEffect(() => {
    if (stillSet) {
      const [{ image_url }] = stillSet;
      setWallpaperURL(image_url);
    } else if (posterSet) {
      const [{ image_url }] = posterSet.filter(({ is_main }) => !is_main);
      setWallpaperURL(image_url);
    }
  }, [stillSet, posterSet]);
  return <Image thumbnail src={wallpaperURL} />;
}

export default function MovieDetailsPage() {
  const { movieId } = useParams();
  const { movie } = useSelector((state) => state.movies);
  const dispatch = useDispatch();

  useEffect(() => {
    retrieveMovie(movieId);
    return () => dispatch(detachMovie());
  }, [movieId, dispatch]);

  return (
    <div>
      <section>
        <Wallpaper />
        <Header />
      </section>
      <MyReviewCard />
      <MovieDetailsCard />
      {JSON.stringify(movie)}
    </div>
  );
}
