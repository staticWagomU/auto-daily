"""Tests for window_monitor module."""

from unittest.mock import MagicMock

from auto_daily.window_monitor import WindowMonitor, get_active_window


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


def test_window_change_detection():
    """ウィンドウ切り替えを検知してイベントを発火できる。"""
    callback = MagicMock()

    monitor = WindowMonitor(on_window_change=callback)

    # 最初のウィンドウ情報をシミュレート
    monitor._current_window = {"app_name": "App1", "window_title": "Title1"}

    # 異なるウィンドウに変更されたことをシミュレート
    new_window = {"app_name": "App2", "window_title": "Title2"}
    monitor._check_window_change(new_window)

    # コールバックが呼ばれたことを確認
    callback.assert_called_once()

    # コールバックには古いウィンドウと新しいウィンドウの情報が渡される
    call_args = callback.call_args[0]
    assert call_args[0] == {"app_name": "App1", "window_title": "Title1"}
    assert call_args[1] == {"app_name": "App2", "window_title": "Title2"}
