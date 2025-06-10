import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, MagicMock
from highway_ingester.github_downloader import download_github_dir, upload_to_s3


@pytest.fixture
def tmp_download_dir(tmp_path):
    return tmp_path / "downloaded_data"


@patch("highway_ingester.github_downloader.requests.get")
def test_download_single_file(mock_get, tmp_download_dir):
    # Simulate GitHub API response for a single file
    mock_api_response = MagicMock()
    mock_api_response.status_code = 200
    mock_api_response.json.return_value = [
        {
            "type": "file",
            "name": "example.csv",
            "download_url": "http://mockurl/file.csv"
        }
    ]

    mock_file_response = MagicMock()
    mock_file_response.status_code = 200
    mock_file_response.content = b"col1,col2\nval1,val2\n"

    # First call is directory listing, second is file content
    mock_get.side_effect = [mock_api_response, mock_file_response]

    download_github_dir(
        repo_owner="dummy",
        repo_name="dummy",
        dir_path="some_path",
        branch="master",
        local_dir=tmp_download_dir
    )

    # Assertions
    expected_file = tmp_download_dir / "example.csv"
    assert expected_file.exists()
    assert expected_file.read_text() == "col1,col2\nval1,val2\n"


@patch("highway_ingester.github_downloader.requests.get")
def test_download_raises_on_404(mock_get, tmp_download_dir):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="404 Not Found"):
        download_github_dir(
            "dummy", "dummy", "wrong_path", local_dir=tmp_download_dir
        )

@patch("highway_ingester.github_downloader.boto3.client")
def test_upload_to_s3_single_file(mock_boto_client, tmp_download_dir):
    # Arrange: create fake file
    tmp_download_dir.mkdir(parents=True, exist_ok=True)
    file_path = tmp_download_dir / "test.csv"
    file_path.write_text("col1,col2\n1,2")

    # Mock S3 client
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    # Act
    upload_to_s3(
        local_dir=tmp_download_dir,
        bucket_name="my-bucket",
        s3_prefix="yellow_tripdata_partitioned_by_day/year=2024/month=1/day=10"
    )

    # Assert
    mock_s3.upload_file.assert_called_once_with(
        str(file_path),
        "my-bucket",
        "yellow_tripdata_partitioned_by_day/year=2024/month=1/day=10/test.csv"
    )


@patch("highway_ingester.github_downloader.boto3.client")
def test_upload_to_s3_empty_dir_warns(mock_boto_client, tmp_download_dir, caplog):
    tmp_download_dir.mkdir(parents=True, exist_ok=True)

    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    with caplog.at_level("WARNING"):
        upload_to_s3(
            local_dir=tmp_download_dir,
            bucket_name="my-bucket",
            s3_prefix="some-prefix"
        )

    assert "No files found" in caplog.text
    mock_s3.upload_file.assert_not_called()