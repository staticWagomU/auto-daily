"""Tests for window_monitor module."""

from auto_daily.window_monitor import get_active_window


def test_get_active_window():
    """AppleScript でアクティブウィンドウのアプリ名とウィンドウタイトルを取得できる。"""
    result = get_active_window()

    # 結果は辞書で、app_name と window_title を含む
    assert isinstance(result, dict)
    assert "app_name" in result
    assert "window_title" in result

    # アプリ名とウィンドウタイトルは文字列である
    assert isinstance(result["app_name"], str)
    assert isinstance(result["window_title"], str)

    # アプリ名は空でない（何かしらのアプリがアクティブなはず）
    assert result["app_name"] != ""
