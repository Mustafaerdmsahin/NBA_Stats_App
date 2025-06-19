from kivy.config import Config


Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'show_mouse', '1')

import logging
from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS['debug'])

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.clock import Clock

import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import numpy as np
import os

def get_current_nba_season_year():
    current_year = datetime.now().year
    current_month = datetime.now().month
    if current_month >= 10: return current_year
    else: return current_year - 1

def get_player_season_stats_nba_api(player_name, season_year):
    Logger.debug(f"API: Veri çekiliyor - Oyuncu: {player_name}, Sezon: {season_year}")
    nba_players = players.get_players()
    matching_players = [player for player in nba_players if player_name.lower() in player['full_name'].lower()]
    if not matching_players:
        Logger.warning(f"API UYARI: '{player_name}' isminde oyuncu bulunamadı.")
        return None
    player_info = matching_players[0]
    player_id = player_info['id']
    player_full_name = player_info['full_name']
    try:
        season_str_for_api = f"{season_year}-{str(season_year + 1)[2:]}"
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        data_frames = career_stats.get_data_frames()
        if len(data_frames) > 0:
            season_averages_df = data_frames[0]
            if season_averages_df.empty: return None
            season_column_name = 'SEASON_ID'
            player_season_data = season_averages_df[season_averages_df[season_column_name] == season_str_for_api]
            if not player_season_data.empty:
                stats_dict = player_season_data.iloc[0].to_dict()
                stats_dict['PLAYER_NAME'] = player_full_name
                Logger.debug(f"API: {player_full_name} için {season_str_for_api} istatistikleri çekildi.")
                return stats_dict
            else:
                Logger.warning(f"API UYARI: {player_full_name} için {season_str_for_api} sezonunda istatistik bulunamadı.")
                return None
        else:
            Logger.error(f"API HATA: playercareerstats endpoint'inden {player_full_name} için DataFrame dönmedi.")
            return None
    except Exception as e:
        Logger.error(f"API HATA: Beklenmeyen bir hata oluştu (Oyuncu: {player_name}, Sezon: {season_year}): {e}")
        return None

def get_multiple_player_season_stats(player_names, seasons):
    all_player_stats = []
    Logger.info("\n--- Çoklu Oyuncu ve Sezon İstatistikleri Çekiliyor ---")
    for player_name in player_names:
        for season_year in seasons:
            stats = get_player_season_stats_nba_api(player_name, season_year)
            if stats: all_player_stats.append(stats)
    if not all_player_stats:
        Logger.warning("Hiçbir oyuncu/sezon için istatistik bulunamadı.")
        return pd.DataFrame()
    final_df = pd.DataFrame(all_player_stats)
    Logger.info("--- Tüm İstatistikler Başarıyla Toplandı ---")
    desired_order = ['PLAYER_NAME', 'SEASON_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 'GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
    actual_order = [col for col in desired_order if col in final_df.columns]
    remaining_columns = [col for col in final_df.columns if col not in actual_order]
    return final_df[actual_order + remaining_columns]

def perform_data_analysis(df):
    analysis_results = []
    if df.empty:
        analysis_results.append("Analiz edilecek veri bulunamadı.")
        return "\n".join(analysis_results)

    analysis_results.append("\n--- Veri Analizi ---")
    stats_columns = ['GP', 'GS', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
                     'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
    existing_stats_columns = [col for col in stats_columns if col in df.columns]

    analysis_results.append("\n1. Genel Tanımlayıcı İstatistikler (Sadece Sayısal Sütunlar):")
    analysis_results.append(df[existing_stats_columns].describe().to_string())

    analysis_results.append("\n2. Oyuncuya Göre Ortalama İstatistikler (Çekilen Sezonlar İçin):")
    player_averages = df.groupby('PLAYER_NAME')[existing_stats_columns].mean()
    analysis_results.append(player_averages.to_string())

    analysis_results.append("\n3. Sezona Göre Ortalama İstatistikler:")
    season_averages = df.groupby('SEASON_ID')[existing_stats_columns].mean()
    analysis_results.append(season_averages.to_string())

    analysis_results.append("\n4. En Yüksek Performanslar (Puan, Asist, Ribaund):")
    if 'PTS' in df.columns:
        top_pts = df.loc[df['PTS'].idxmax()]
        analysis_results.append(f"En Yüksek Puan (PTS): {top_pts['PTS']} - Oyuncu: {top_pts['PLAYER_NAME']}, Sezon: {top_pts['SEASON_ID']}")
    if 'AST' in df.columns:
        top_ast = df.loc[df['AST'].idxmax()]
        analysis_results.append(f"En Yüksek Asist (AST): {top_ast['AST']} - Oyuncu: {top_ast['PLAYER_NAME']}, Sezon: {top_ast['SEASON_ID']}")
    if 'REB' in df.columns:
        top_reb = df.loc[df['REB'].idxmax()]
        analysis_results.append(f"En Yüksek Ribaund (REB): {top_reb['REB']} - Oyuncu: {top_reb['PLAYER_NAME']}, Sezon: {top_reb['SEASON_ID']}")

    analysis_results.append("\n5. Oyuncuların Üç Sayılık Yüzdeleri (FG3_PCT) - Çekilen Sezonlar İçin:")
    if 'FG3_PCT' in df.columns:
        fg3_pct_sorted = df[['PLAYER_NAME', 'SEASON_ID', 'FG3_PCT']].sort_values(by='FG3_PCT', ascending=False)
        analysis_results.append(fg3_pct_sorted.to_string(index=False))
        analysis_results.append("\nHer Oyuncunun En Yüksek 3 Sayılık Yüzdesi:")
        for player_name in df['PLAYER_NAME'].unique():
            player_df = df[df['PLAYER_NAME'] == player_name]
            best_fg3_pct = player_df.loc[player_df['FG3_PCT'].idxmax()]
            analysis_results.append(f"- {player_name}: {best_fg3_pct['FG3_PCT']:.3f} ({best_fg3_pct['SEASON_ID']})")

    if 'PTS' in df.columns and 'GP' in df.columns:
        df['PTS_PER_GAME'] = df['PTS'] / df['GP']
        analysis_results.append("\nMaç Başına Puan Ortalamaları (Hesaplandı):")
        analysis_results.append(df[['PLAYER_NAME', 'SEASON_ID', 'PTS_PER_GAME']].to_string(index=False))

    analysis_results.append("--- Veri Analizi Tamamlandı ---")
    return "\n".join(analysis_results)

class NBAStatsApp(App):
    def build(self):
        Logger.info("Uygulama: build metodu başlatıldı.")
        self.title = 'NBA İstatistik Uygulaması'

        self.main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Widget'ların yükseklikleri size_hint_y ile orantısal olarak ayarlandı
        self.main_layout.add_widget(Label(text="Oyuncu Adı (Virgülle Ayırın):", size_hint_y=0.08))
        self.player_input = TextInput(hint_text="örn: Stephen Curry, LeBron James", multiline=False, size_hint_y=0.10)
        self.main_layout.add_widget(self.player_input)

        self.main_layout.add_widget(Label(text="Sezon Aralığı (YYYY-YYYY veya YYYY):", size_hint_y=0.08))
        self.season_input = TextInput(hint_text="örn: 2020-2023 veya 2023", multiline=False, size_hint_y=0.10)
        self.main_layout.add_widget(self.season_input)

        self.fetch_button = Button(text="İstatistikleri Getir", size_hint_y=0.12)
        self.fetch_button.bind(on_release=self.on_fetch_button_press)
        self.main_layout.add_widget(self.fetch_button)

        self.status_label = Label(text="", size_hint_y=0.08, color=[1,0,0,1])
        self.main_layout.add_widget(self.status_label)

        # ScrollView kalan alanı dolduracak şekilde ayarlandı
        self.results_scroll_view = ScrollView(size_hint_y=0.44)
        self.results_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_scroll_view.add_widget(self.results_layout)
        self.main_layout.add_widget(self.results_scroll_view)

        Logger.info("Uygulama: build metodu tamamlandı. UI hazır.")
        return self.main_layout

    def on_fetch_button_press(self, instance):
        Logger.info("Uygulama: Butona basıldı.")
        player_names_raw = self.player_input.text
        season_range_raw = self.season_input.text

        self.status_label.text = "Veriler çekiliyor..."
        self.results_layout.clear_widgets()

        player_names_to_fetch = [name.strip() for name in player_names_raw.split(',') if name.strip()]

        if not player_names_to_fetch:
            self.status_label.text = "Lütfen geçerli bir oyuncu adı girin."
            Logger.warning("Uygulama: Oyuncu adı girilmedi.")
            return

        seasons_to_fetch = []
        if '-' in season_range_raw:
            try:
                start_year_str, end_year_str = season_range_raw.split('-')
                start_year = int(start_year_str.strip())
                end_year = int(end_year_str.strip())
                if start_year > end_year:
                    self.status_label.text = "Hata: Başlangıç yılı bitiş yılından büyük olamaz."
                    Logger.error("Uygulama: Sezon aralığı hatası - Başlangıç yılı > bitiş yılı.")
                    return
                seasons_to_fetch = list(range(start_year, end_year + 1))
            except ValueError:
                self.status_label.text = "Hata: Sezon aralığı formatı yanlış (YYYY-YYYY)."
                Logger.error("Uygulama: Sezon aralığı format hatası (YYYY-YYYY).")
                return
        else:
            try:
                single_season = int(season_range_raw.strip())
                seasons_to_fetch = [single_season]
            except ValueError:
                self.status_label.text = "Hata: Sezon formatı yanlış (YYYY)."
                Logger.error("Uygulama: Sezon format hatası (YYYY).")
                return

        import threading
        thread = threading.Thread(target=self._fetch_and_display_stats, args=(player_names_to_fetch, seasons_to_fetch))
        thread.daemon = True
        thread.start()
        Logger.info("Uygulama: Veri çekme thread'i başlatıldı.")

    def _fetch_and_display_stats(self, player_names, seasons):
        try:
            Logger.info("Thread: Veri çekme işlemi başladı.")
            all_stats_df = get_multiple_player_season_stats(player_names, seasons)
            Logger.info("Thread: Veri çekme işlemi tamamlandı.")

            if not all_stats_df.empty:
                stats_display_text = "Çekilen İstatistikler (Raw):\n" + all_stats_df.to_string(index=False)
                analysis_text = perform_data_analysis(all_stats_df)
                final_output_text = stats_display_text + "\n\n" + analysis_text

                Clock.schedule_once(lambda dt: self._update_ui_with_results(final_output_text, "Veriler başarıyla yüklendi."), 0)
                Logger.info("Thread: UI güncelleme planlandı (Başarılı).")
            else:
                Clock.schedule_once(lambda dt: self._update_ui_with_results("Hiçbir istatistik bulunamadı. Lütfen oyuncu adını ve sezonu kontrol edin.", "Hata: Veri bulunamadı."), 0)
                Logger.warning("Thread: Hiç veri bulunamadı. UI güncelleme planlandı (Uyarı).")
        except Exception as e:
            Logger.exception("Thread HATA: Veri çekme veya işleme sırasında beklenmeyen bir hata oluştu.")
            Clock.schedule_once(lambda dt: self._update_ui_with_results(f"Beklenmeyen bir hata oluştu: {e}", "Hata: Uygulama hatası."), 0)

    def _update_ui_with_results(self, result_text, status_message):
        Logger.info(f"UI: Sonuçlar güncelleniyor. Durum: {status_message}")
        self.results_layout.clear_widgets()

        result_label = Label(text=result_text, size_hint_y=None, halign='left', valign='top',
                             text_size=(self.results_layout.width, None))

        def _set_label_height(instance, texture_size):
            instance.height = texture_size[1]

        result_label.bind(texture_size=_set_label_height)

        self.results_layout.add_widget(result_label)
        self.status_label.text = status_message
        Logger.info("UI: Sonuçlar güncellendi.")

if __name__ == '__main__':
    Logger.info("Uygulama: Başlatılıyor...")
    NBAStatsApp().run()
    Logger.info("Uygulama: Kapandı.")