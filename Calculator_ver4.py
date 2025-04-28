#계산기끼리 충돌안나게 하기
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="GFI & FuelEU 계산기", layout="centered")

# 메뉴
menu = st.sidebar.radio("계산 항목 선택", ["GFI 계산기", "FuelEU Maritime"])
#menu = st.sidebar.radio("계산 항목 선택", ["GFI 계산기", "FuelEU Maritime", "CII (준비 중)", "EU ETS (준비 중)"])

# 연료 기본값 (GFI 계산기와 FuelEU 계산기 공통)
fuel_defaults = {
    "VLSFO": {"LHV": 40500, "WtW": 91.60123},
    "HSFO":  {"LHV": 40500, "WtW": 91.60123},
    "LSMGO": {"LHV": 42700, "WtW": 90.63185},
    "LNG":   {"LHV": 49100, "WtW": 76.12916},
    "B24":   {"LHV": 39708, "WtW": 74.28817013},
    "B30":   {"LHV": 39510, "WtW": 69.85145205},
    "B100":  {"LHV": 37200, "WtW": 14.60},
}

# 🌱 GFI 계산기
if menu == "GFI 계산기":
    st.title("🌱 GFI 계산기")

    if "fuel_data" not in st.session_state:
        st.session_state["fuel_data"] = []
    if "edit_index" not in st.session_state:
        st.session_state["edit_index"] = None
    if "manual_mode" not in st.session_state:
        st.session_state["manual_mode"] = False
    if "gfi_calculated" not in st.session_state:
        st.session_state["gfi_calculated"] = False

    # 연료 수정
    if st.session_state["edit_index"] is not None:
        st.subheader("✏️ 연료 수정")
        edit_row = st.session_state.fuel_data[st.session_state["edit_index"]]
        with st.form("edit_form"):
            fuel_type = st.selectbox("연료 종류", list(fuel_defaults.keys()),
                                     index=list(fuel_defaults.keys()).index(edit_row["연료종류"]))
            lhv = st.number_input("저위발열량 (MJ/Ton)", value=float(edit_row["LHV"]), min_value=0.0)
            wtw = st.number_input("Well-to-Wake 계수 (gCO₂eq/MJ)", value=float(edit_row["WtW"]), min_value=0.0)
            amount = st.number_input("사용량 (톤)", value=float(edit_row["사용량"]), min_value=0.0)
            submitted = st.form_submit_button("수정 완료")
            if submitted:
                st.session_state.fuel_data[st.session_state["edit_index"]] = {
                    "연료종류": fuel_type,
                    "LHV": lhv,
                    "WtW": wtw,
                    "사용량": amount
                }
                st.session_state["edit_index"] = None
                st.rerun()

    # 연료 추가
    else:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader("➕ 연료 추가")
        with col2:
            button_label = "🔄 자동 입력" if st.session_state["manual_mode"] else "🔄 수동 입력"
            if st.button(button_label):
                st.session_state["manual_mode"] = not st.session_state["manual_mode"]
                st.rerun()
        with st.form("fuel_form"):
            fuel_type = st.selectbox("연료 종류", list(fuel_defaults.keys()))
            if st.session_state["manual_mode"]:
                lhv = st.number_input("저위발열량 (MJ/Ton)", min_value=0.0)
                wtw = st.number_input("Well-to-Wake 계수 (gCO₂eq/MJ)", min_value=0.0)
            else:
                lhv = fuel_defaults[fuel_type]["LHV"]
                wtw = fuel_defaults[fuel_type]["WtW"]
            amount = st.number_input("사용량 (톤)", min_value=0.0)
            submitted = st.form_submit_button("연료 추가")
            if submitted:
                st.session_state.fuel_data.append({
                    "연료종류": fuel_type,
                    "LHV": lhv,
                    "WtW": wtw,
                    "사용량": amount
                })
                st.rerun()

    # 입력한 연료 목록
    st.divider()
    st.subheader("📋 입력한 연료 목록")
    delete_indices = []
    for i, row in enumerate(st.session_state.fuel_data, start=1):
        cols = st.columns([0.5, 1, 2, 2, 2, 2, 1])
        with cols[0]:
            selected = st.checkbox("", key=f"check_{i}")
        with cols[1]:
            st.write(f"{i}")
        with cols[2]:
            st.write(row["연료종류"])
        with cols[3]:
            st.write(row["LHV"])
        with cols[4]:
            st.write(row["WtW"])
        with cols[5]:
            st.write(row["사용량"])
        with cols[6]:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state["edit_index"] = i - 1
                st.rerun()
        if selected:
            delete_indices.append(i - 1)

    if delete_indices:
        if st.button("🗑️ 선택한 연료 삭제"):
            for index in sorted(delete_indices, reverse=True):
                st.session_state.fuel_data.pop(index)
            st.session_state["edit_index"] = None
            st.rerun()

    # GFI 계산 버튼
    if st.button("GFI 계산하기"):
        if st.session_state.fuel_data:
            st.session_state["gfi_calculated"] = True
        else:
            st.warning("연료를 먼저 입력해주세요.")

    # 계산 결과 표시
    if st.session_state["gfi_calculated"] and st.session_state.fuel_data:
        # ✨ 여기에 기존 GFI 계산기 로직 (그래프, 표 등) 붙이면 됨
        df = pd.DataFrame(st.session_state.fuel_data)
        if not df.empty:
            df["총배출량(tCO2eq)"] = df["LHV"] * df["WtW"] * df["사용량"] * 1e-3
            df["총에너지(MJ)"] = df["LHV"] * df["사용량"]
            total_emission = df["총배출량(tCO2eq)"].sum()
            total_energy = df["총에너지(MJ)"].sum()
            gfi = (total_emission * 1000) / total_energy
            st.success(f"계산된 GFI: **{gfi:.2f} gCO₂eq/MJ**")

            years = list(range(2028, 2036))
            base_gfi = [round(93.3 * r, 5) for r in [0.96, 0.94, 0.92, 0.877, 0.832, 0.788, 0.744, 0.7]]
            direct_gfi = [93.3*(1-0.17),93.3*(1-0.19),93.3*(1-0.21),93.3*(1-0.254),93.3*(1-0.298),93.3*(1-0.342),93.3*(1-0.386),93.3*(1-0.43)]

            # ZNZ 기준선 추가 (연도별 19.0 or 14.0)
            znz = [19.0 if year <= 2034 else 14.0 for year in years]

            # 그래프 시각화
            plt.figure(figsize=(8, 4))
            plt.plot(years, base_gfi, label="Base GFI", linestyle="--", marker="o")
            plt.plot(years, direct_gfi, label="Direct GFI", linestyle=":", marker="o")
            plt.hlines(gfi, 2028, 2035, color="red", linestyles="-", label=f"Your GFI: {gfi:.2f}")
            
            # ✅ ZNZ 선 추가
            plt.step(years, znz, where='post', label="ZNZ 기준선", color="gold", linewidth=2)
            
            # ✅ 숫자 표기 (ZNZ)
            for x, y in zip(years, znz):
                plt.text(x, y + 1, f"{y:.1f}", ha='center', va='bottom', fontsize=8, color="gold")

            # 나머지 텍스트
            for x, y in zip(years, base_gfi):
                plt.text(x, y + 1, f"{y:.1f}", ha='center', va='bottom', fontsize=8)
            for x, y in zip(years, direct_gfi):
                plt.text(x, y + 1, f"{y:.1f}", ha='center', va='bottom', fontsize=8)
            plt.xlabel("연도")
            plt.ylabel("gCO₂eq/MJ")
            plt.title("GFI vs 기준 GFI")
            plt.legend()
            st.pyplot(plt)

            # Compliance 결과 테이블
            data = []
            surplus_data = []
            for i, (y, bg, dg) in enumerate(zip(years, base_gfi, direct_gfi), start=1):
                row = {"No.": i, "연도": y}
                total_penalty = 0

                if gfi > bg:
                    row["Tier"] = "Tier 2"
                    cb1 = round(round(bg - dg, 5) * round(total_energy, 2) / 1e6, 2)
                    cb2 = round(round(gfi - bg, 5) * round(total_energy, 2) / 1e6, 2)
                    p1 = round(cb1 * 100, 0)
                    p2 = round(cb2 * 380, 1)
                    total_penalty = p1 + p2
                    row["Tier 1 CB (tCO₂eq)"] = f"{cb1:,.2f} tCO₂eq"
                    row["Tier 2 CB (tCO₂eq)"] = f"{cb2:,.2f} tCO₂eq"
                    row["Tier 1 Penalty ($)"] = f"${p1:,.0f}"
                    row["Tier 2 Penalty ($)"] = f"${p2:,.1f}"

                elif gfi > dg:
                    row["Tier"] = "Tier 1"
                    cb1 = round(round(gfi - dg, 5) * round(total_energy, 2) / 1e6, 2)
                    p1 = round(cb1 * 100, 0)
                    total_penalty = p1
                    row["Tier 1 CB (tCO₂eq)"] = f"{cb1:,.2f} tCO₂eq"
                    row["Tier 1 Penalty ($)"] = f"${p1:,.0f}"

                else:
                    row["Tier"] = "Surplus"
                    surplus = round(round(dg - gfi, 5) * round(total_energy, 2) / 1e6, 2)
                    row["Surplus (tCO₂eq)"] = f"{surplus:,.2f} tCO₂eq"
                    surplus_data.append({"연도": y, "Surplus (tCO₂eq)": f"{surplus:,.2f} tCO₂eq"})

                if row["Tier"] != "Surplus":
                    row["Total Penalty ($)"] = f"${total_penalty:,.1f}"
                else:
                    row["Total Penalty ($)"] = "None"

                data.append(row)

            # ✅ 열 순서 지정
            columns_order = ["No.", "연도", "Tier",
                 "Tier 1 CB (tCO₂eq)", "Tier 1 Penalty ($)",
                 "Tier 2 CB (tCO₂eq)", "Tier 2 Penalty ($)",
                 "Surplus (tCO₂eq)", "Total Penalty ($)"]

            df_result = pd.DataFrame(data)
            df_result = df_result.reindex(columns=[col for col in columns_order if col in df_result.columns])

            st.subheader("📘 연도별 Compliance 결과")
            st.dataframe(df_result, use_container_width=True, hide_index=True)

            if surplus_data:
                st.subheader("🟢 Surplus 발생 연도")
                st.dataframe(pd.DataFrame(surplus_data), use_container_width=True, hide_index=True)

                st.subheader("🔄 Surplus로 상쇄 가능한 연료 사용량 (톤)")

                fuel_gfi_lhv = {
        "VLSFO": {"GFI": 91.60123, "LHV": 40500},
        "HSFO":  {"GFI": 91.60123, "LHV": 40500},
        "LSMGO": {"GFI": 90.63185, "LHV": 42700},
        "LNG":   {"GFI": 76.12916, "LHV": 49100},
        "B24":   {"GFI": 74.28817013, "LHV": 39708},
        "B30":   {"GFI": 69.85145205, "LHV": 39510},
        "B100":  {"GFI": 14.6, "LHV": 37200},
    }

                base_gfi_dict = dict(zip(years, base_gfi))

                offset_table = {"연도": []}
                for fuel in fuel_gfi_lhv.keys():
                    offset_table[fuel] = []

                for entry in surplus_data:
                    year = entry["연도"]
                    surplus_str = entry["Surplus (tCO₂eq)"]
                    surplus = float(surplus_str.replace(",", "").split()[0])
                    base = base_gfi_dict[year]

                    offset_table["연도"].append(year)

                    for fuel, info in fuel_gfi_lhv.items():
                        delta_gfi = info["GFI"] - base
                        if delta_gfi > 0:
                            energy_mj = surplus * 1_000_000 / delta_gfi
                            tonnage = energy_mj / info["LHV"]
                            offset_table[fuel].append(round(tonnage, 2))
                        else:
                            offset_table[fuel].append(0.0)

                df_offset_wide = pd.DataFrame(offset_table)
                st.dataframe(df_offset_wide, use_container_width=True, hide_index=True)

            
            # ✅ Tier 2 상쇄용 친환경 연료 사용량 계산 (연도별)
            if gfi > min(base_gfi):  # GFI가 최소 기준 GFI보다 클 때만 계산

                st.subheader("🌿 Tier 2 Penalty 상쇄를 위한 친환경 연료 사용량 (톤)")

                green_fuels = {
        "LNG":  {"GFI": 76.12916, "LHV": 49100},
        "B24":  {"GFI": 74.28817013, "LHV": 39708},
        "B30":  {"GFI": 69.85145205, "LHV": 39510},
        "B100": {"GFI": 14.60, "LHV": 37200},
    }

                data_tier2 = {"연도": []}
                data_tier1 = {"연도": []}
                for fuel in green_fuels:
                    data_tier2[fuel] = []
                    data_tier1[fuel] = []

                for i, year in enumerate(years):
                    bg = base_gfi[i]
                    dg = direct_gfi[i]

                    if gfi > bg:
                        cb2 = (gfi - bg) * total_energy / 1e6  # Tier2 CB (tCO₂eq)
                        cb1 = (bg - dg) * total_energy / 1e6   # Tier1 CB (tCO₂eq)

                        data_tier2["연도"].append(year)
                        data_tier1["연도"].append(year)

                        for fuel, info in green_fuels.items():
                            delta_gfi_t2 = bg - info["GFI"]
                            delta_gfi_t1 = dg - info["GFI"]

                            t2 = cb2 * 1_000_000 / delta_gfi_t2 / info["LHV"] if delta_gfi_t2 > 0 else 0
                            t1 = cb1 * 1_000_000 / delta_gfi_t1 / info["LHV"] if delta_gfi_t1 > 0 else 0

                            data_tier2[fuel].append(round(t2, 2))
                            data_tier1[fuel].append(round(t1, 2))

                df_t2 = pd.DataFrame(data_tier2)
                df_t1 = pd.DataFrame(data_tier1)

                st.write("✅ Tier 2 벌금 전액 상쇄에 필요한 연료량 (톤)")
                st.dataframe(df_t2, use_container_width=True, hide_index=True)

                st.write("✅ Tier 1 수준으로 진입하기 위한 연료량 (톤)")
                st.dataframe(df_t1, use_container_width=True, hide_index=True)


        else:
            st.warning("먼저 연료를 입력해주세요.")
        
# 🚢 FuelEU Maritime 계산기
elif menu == "FuelEU Maritime":
    st.title("🚢 FuelEU Maritime 계산기")

    if "fueleu_data" not in st.session_state:
        st.session_state["fueleu_data"] = []
    if "fueleu_edit_index" not in st.session_state:
        st.session_state["fueleu_edit_index"] = None
    if "fueleu_manual_mode" not in st.session_state:
        st.session_state["fueleu_manual_mode"] = False
    if "fueleu_calculated" not in st.session_state:
        st.session_state["fueleu_calculated"] = False

    # 연료 추가
    col1, col2 = st.columns([5, 1])
    with col1:
        st.subheader("➕ 연료 추가")
    with col2:
        button_label = "🔄 자동 입력" if st.session_state["fueleu_manual_mode"] else "🔄 수동 입력"
        if st.button(button_label):
            st.session_state["fueleu_manual_mode"] = not st.session_state["fueleu_manual_mode"]
            st.session_state["fueleu_calculated"] = False
            st.rerun()

    if st.session_state["fueleu_edit_index"] is not None:
        st.subheader("✏️ 연료 수정")
        row = st.session_state["fueleu_data"][st.session_state["fueleu_edit_index"]]
        with st.form("fueleu_edit_form"):
            fuel_type = st.selectbox("연료 종류", list(fuel_defaults.keys()), index=list(fuel_defaults.keys()).index(row["연료종류"]))
            lhv = st.number_input("저위발열량 (MJ/Ton)", value=float(row["LHV"]), min_value=0.0)
            gfi = st.number_input("GFI (gCO₂eq/MJ)", value=float(row["GFI"]), min_value=0.0)
            inside = st.number_input("역내 사용량 (톤)", value=float(row["역내"]), min_value=0.0)
            outside = st.number_input("역외 사용량 (톤)", value=float(row["역외"]), min_value=0.0)
            submitted = st.form_submit_button("수정 완료")
            if submitted:
                st.session_state["fueleu_data"][st.session_state["fueleu_edit_index"]] = {
                    "연료종류": fuel_type,
                    "LHV": lhv,
                    "GFI": gfi,
                    "역내": inside,
                    "역외": outside
                }
                st.session_state["fueleu_edit_index"] = None
                st.session_state["fueleu_calculated"] = False
                st.rerun()

    else:
        with st.form("fueleu_add_form"):
            fuel_type = st.selectbox("연료 종류", list(fuel_defaults.keys()))
            if st.session_state["fueleu_manual_mode"]:
                lhv = st.number_input("저위발열량 (MJ/Ton)", min_value=0.0)
                gfi = st.number_input("GFI (gCO₂eq/MJ)", min_value=0.0)
            else:
                lhv = fuel_defaults[fuel_type]["LHV"]
                gfi = fuel_defaults[fuel_type]["WtW"]
            inside = st.number_input("역내 사용량 (톤)", min_value=0.0)
            outside = st.number_input("역외 사용량 (톤)", min_value=0.0)
            submitted = st.form_submit_button("연료 추가")
            if submitted:
                st.session_state["fueleu_data"].append({
                    "연료종류": fuel_type,
                    "LHV": lhv,
                    "GFI": gfi,
                    "역내": inside,
                    "역외": outside
                })
                st.session_state["fueleu_calculated"] = False
                st.rerun()

    st.divider()
    st.subheader("📋 입력한 연료 목록")

    delete_indices = []
    for i, row in enumerate(st.session_state["fueleu_data"], start=1):
        cols = st.columns([0.5, 1, 2, 2, 2, 2, 2, 1])
        with cols[0]:
            selected = st.checkbox("", key=f"feu_check_{i}")
        with cols[1]:
            st.write(f"{i}")
        with cols[2]:
            st.write(row["연료종류"])
        with cols[3]:
            st.markdown(f"<span style='color: green;'>{row['LHV']:,}</span>", unsafe_allow_html=True)
        with cols[4]:
            st.markdown(f"<span style='color: green;'>{row['GFI']:,}</span>", unsafe_allow_html=True)
        with cols[5]:
            st.markdown(f"<span style='color: green;'>{row['역내']:,}</span>", unsafe_allow_html=True)
        with cols[6]:
            st.markdown(f"<span style='color: green;'>{row['역외']:,}</span>", unsafe_allow_html=True)
        with cols[7]:
            if st.button("✏️", key=f"feu_edit_{i}"):
                st.session_state["fueleu_edit_index"] = i - 1
                st.rerun()
        if selected:
            delete_indices.append(i - 1)

    if delete_indices:
        if st.button("🗑️ 선택한 연료 삭제"):
            for index in sorted(delete_indices, reverse=True):
                st.session_state["fueleu_data"].pop(index)
            st.session_state["fueleu_edit_index"] = None
            st.session_state["fueleu_calculated"] = False
            st.rerun()

    if st.button("FuelEU 계산하기"):
        if st.session_state["fueleu_data"]:
            st.session_state["fueleu_calculated"] = True
        else:
            st.warning("연료를 먼저 입력해주세요.")

    if st.session_state["fueleu_calculated"] and st.session_state["fueleu_data"]:
        st.success("FuelEU 계산 완료")

        df = pd.DataFrame(st.session_state["fueleu_data"])

        # B24, B30 분리
        expanded_rows = []
        for _, row in df.iterrows():
            if row["연료종류"] == "B24":
                expanded_rows.append({"연료종류": "VLSFO", "LHV": 40500, "GFI": 91.60123, "역내": row["역내"] * 0.76, "역외": row["역외"] * 0.76})
                expanded_rows.append({"연료종류": "B100",  "LHV": 37200, "GFI": 14.6, "역내": row["역내"] * 0.24, "역외": row["역외"] * 0.24})
            elif row["연료종류"] == "B30":
                expanded_rows.append({"연료종류": "VLSFO", "LHV": 40500, "GFI": 91.60123, "역내": row["역내"] * 0.7, "역외": row["역외"] * 0.7})
                expanded_rows.append({"연료종류": "B100",  "LHV": 37200, "GFI": 14.6, "역내": row["역내"] * 0.3, "역외": row["역외"] * 0.3})
            else:
                expanded_rows.append({
            "연료종류": row["연료종류"],
            "LHV": row["LHV"],
            "GFI": row["GFI"],
            "역내": row["역내"],
            "역외": row["역외"]
        })

        df_expanded = pd.DataFrame(expanded_rows)

        # 벌금 기준 발열량 계산
        df_expanded["역내_LHV"] = df_expanded["역내"] * df_expanded["LHV"]
        df_expanded["역외_LHV"] = df_expanded["역외"] * df_expanded["LHV"] * 0.5
        penalty_basis_energy = df_expanded["역내_LHV"].sum() + df_expanded["역외_LHV"].sum()

        # 채워넣을 발열량 (친환경연료는 100% 인정)
        def calc_adjusted_outside(row):
            if row["연료종류"] in ["LNG", "B100"]:
                return row["역외"] * row["LHV"]  # 100% 인정
            else:
                return row["역외"] * row["LHV"] * 0.5  # 50% 인정

        df_expanded["adj_outside_LHV"] = df_expanded.apply(calc_adjusted_outside, axis=1)
        df_expanded["total_adj_LHV"] = df_expanded["역내_LHV"] + df_expanded["adj_outside_LHV"]

        # GFI 낮은 순 정렬
        df_sorted = df_expanded.sort_values(by="GFI").reset_index(drop=True)

        # 발열량 채워넣기
        cumulative_energy = 0
        selected_rows = []
        for _, row in df_sorted.iterrows():
            if cumulative_energy + row["total_adj_LHV"] <= penalty_basis_energy:
                used_energy = row["total_adj_LHV"]
            else:
                used_energy = penalty_basis_energy - cumulative_energy
                if used_energy <= 0:
                    break
            cumulative_energy += used_energy
            selected_rows.append((row, used_energy))

        # 결과 정리
        table = []
        total_energy = 0
        total_emission = 0
        for idx, (row, used_energy) in enumerate(selected_rows, start=1):
            ghg_intensity = row["GFI"]
            emission = used_energy * ghg_intensity / 1_000_000  # tCO₂eq
            table.append({
                "No.": idx,
                "연료종류": row["연료종류"],
                "GHG Intensity (gCO₂eq/MJ)": round(ghg_intensity, 3),
                "반영 LCV (MJ)": round(used_energy, 3),
                "배출량 (tCO₂eq)": round(emission, 3)
            })
            total_energy += used_energy
            total_emission += emission
                
        # 평균 GHG Intensity
        avg_ghg_intensity = (total_emission * 1_000_000 / total_energy) if total_energy > 0 else 0
        avg_ghg_intensity = round(avg_ghg_intensity, 3)
        
        st.subheader("📄 FuelEU Maritime 계산 결과")
        
        # 2️⃣ 여기서부터만 수정
        df_result = pd.DataFrame(table)

        # ✅ Total 행 추가
        df_result.loc["합계"] = {
    "No.": "-",
    "연료종류": "Total",
    "GHG Intensity (gCO₂eq/MJ)": f"{avg_ghg_intensity:,.3f}",
    "반영 LCV (MJ)": f"{total_energy:,.3f}",
    "배출량 (tCO₂eq)": f"{total_emission:,.3f}"
}

        # ✅ 숫자 포맷 적용
        for col in ["GHG Intensity (gCO₂eq/MJ)", "반영 LCV (MJ)", "배출량 (tCO₂eq)"]:
            df_result[col] = df_result[col].apply(lambda x: f"{x:,.3f}" if isinstance(x, (int, float)) else x)

        # 3️⃣ 출력
        st.dataframe(df_result, use_container_width=True, hide_index=True)
        
        steps = [
            (2025, 2029, round(91.16 * 0.98, 2)),
            (2030, 2034, round(91.16 * 0.94, 2)),
            (2035, 2039, round(91.16 * (1 - 0.145), 2)),
            (2040, 2044, round(91.16 * (1 - 0.31), 2)),
            (2045, 2049, round(91.16 * (1 - 0.62), 2)),
            (2050, 2050, round(91.16 * 0.2, 2)),
        ]
        
        standards = [round(91.16 * 0.98, 2),
             round(91.16 * 0.94, 2),
             round(91.16 * (1 - 0.145), 2),
             round(91.16 * (1 - 0.31), 2),
             round(91.16 * (1 - 0.62), 2),
             round(91.16 * 0.8, 2)]

        # CB 및 Penalty 계산
        standard_now = standards[0]  # 2025년 기준
        delta_ghg = avg_ghg_intensity - standard_now
        cb = delta_ghg * total_energy / 1_000_000
        penalty_eur = delta_ghg * total_energy * 2400 / 41000 / avg_ghg_intensity

        cb = round(cb, 3)
        penalty_eur = round(penalty_eur, 3)

        # 결과 출력
        
        df_result = pd.DataFrame(table)
        df_result.loc["합계"] = ["-", "-", f"{total_energy:,.3f}", f"{total_emission:,.3f}", "-"]

        st.write(f"**평균 GHG Intensity:** {avg_ghg_intensity:,.3f} gCO₂eq/MJ")
        st.write(f"**기준 GHG Intensity (2025):** {standard_now:,.2f} gCO₂eq/MJ")
        st.write(f"**Compliance Balance (CB):** {cb:,.3f} tCO₂eq")
        st.write(f"**예상 벌금:** € {penalty_eur:,.3f}")

        years = []
        standard_values = []

        for start, end, value in steps:
            for year in range(start, end + 1):
                years.append(year)
                standard_values.append(value)

        st.subheader("📈 GHG Intensity 기준선 vs 평균 GHG Intensity")

        plt.figure(figsize=(10, 4))
        plt.step(years, standard_values, where='post', label="기준 GHG Intensity", color="blue", linewidth=2)
        plt.hlines(avg_ghg_intensity, 2025, 2050, colors="red", linestyles="--", label=f"계산된 평균: {avg_ghg_intensity} gCO₂eq/MJ")

        for start, end, value in steps:
            plt.text(start, value + 1, f"{value:.1f}", ha='left', va='bottom', fontsize=8, color="blue")

        plt.xlabel("연도")
        plt.ylabel("gCO₂eq/MJ")
        plt.title("FuelEU Maritime - GHG Intensity 비교")
        plt.xticks(range(2025, 2051, 5))
        plt.legend()
        st.pyplot(plt)
    
            # 📘 연도별 Compliance 결과 계산
        st.subheader("📘 연도별 Compliance 결과")

        compliance_data = []
        deficit_rows = []
        surplus_rows = []

        for year, std_value in zip(years, standard_values):
            delta = avg_ghg_intensity - std_value
            cb_year = delta * total_energy / 1_000_000  # (tCO₂eq)

            if delta > 0:
                tier = "Deficit"
                penalty = delta * total_energy * 2400 / 41000 / avg_ghg_intensity
            else:
                tier = "Surplus"
                penalty = 0

            compliance_data.append({
                "연도": year,
                "Tier": tier,
                "CB (tCO₂eq)": round(cb_year, 3),
                "Penalty (€)": f"{penalty:,.1f}" if penalty else "-"
            })

            # Deficit / Surplus 테이블용
            if delta > 0:
                deficit_rows.append((year, cb_year))
            elif delta < 0:
                surplus_rows.append((year, abs(cb_year)))

        df_compliance = pd.DataFrame(compliance_data)
        st.dataframe(df_compliance, use_container_width=True, hide_index=True)

                        # ==================== 🌿 Deficit: 추가 친환경 연료 사용량 ====================
        if deficit_rows:
                st.subheader("🌿 Deficit 해소를 위한 추가 친환경 연료 사용량 (톤)")

                green_fuels = {
                        "LNG":  {"GFI": 76.12916, "LHV": 49100},
                        "B24":  {"GFI": 74.28817013, "LHV": 39708},
                        "B30":  {"GFI": 69.85145205, "LHV": 39510},
                        "B100": {"GFI": 14.60, "LHV": 37200},
                }

                data_deficit = {"연료 종류": [], "역내-추가 사용 가능(톤)": [], "역외-추가 사용 가능(톤)": []}

                for fuel, info in green_fuels.items():
                        # 역내 추가 사용량 계산 (기존 방식)
                        delta_ghg = standard_now - info["GFI"]
                        if delta_ghg > 0:
                                allowed_energy = cb * 1_000_000 / delta_ghg  # MJ
                                tons_possible_in = allowed_energy / info["LHV"]  # 역내 추가 사용량 (톤)
                        else:
                                tons_possible_in = 0

                        # ✅ 역외 추가 사용량 계산 (Deficit 0 만들기 위한 정밀 계산)
                        if fuel in ["B24", "B30"]:
                                # 혼합비율 설정
                                if fuel == "B24":
                                        vlsfo_ratio = 0.76
                                        b100_ratio = 0.24
                                else:  # B30
                                        vlsfo_ratio = 0.70
                                        b100_ratio = 0.30

                                # 기본 정보
                                vlsfo_lhv = 40500
                                b100_lhv = 37200
                                vlsfo_gfi = 91.60123
                                b100_gfi = 14.6

                                # 🔥 수정된 계산법
                                numerator = (standard_now * total_energy) - (total_emission * 1_000_000)
                                denominator = (
                                        (b100_ratio * b100_lhv * (b100_gfi - standard_now)) +
                                        (0.5 * (1 - b100_ratio) * vlsfo_lhv * (vlsfo_gfi - standard_now))
                                )

                                if denominator != 0:
                                        tons_possible_out = numerator / denominator
                                else:
                                        tons_possible_out = 0

                                tons_possible_out = max(tons_possible_out, 0)

                        else:
                                # LNG 또는 B100
                                # 여기에 엑셀 수식 기반 Deficit 0 계산 적용
                                if penalty_eur > 0:  # Penalty가 있는 경우
                                        base_out = penalty_basis_energy / info["LHV"] * 2

                                        numerator = (standard_now * penalty_basis_energy) - (total_emission * 1_000_000)
                                        denominator = (
                                                (info["GFI"] * info["LHV"]) -
                                                (0.5 * avg_ghg_intensity * info["LHV"]) -
                                                (0.5 * standard_now * info["LHV"])
                                        )

                                        if denominator != 0:
                                                accurate_out = numerator / denominator
                                        else:
                                                accurate_out = base_out

                                        tons_possible_out = min(base_out, accurate_out)
                                        tons_possible_out = max(tons_possible_out, 0)

                                else:
                                        tons_possible_out = 0

                        # ✅ 테이블 저장
                        data_deficit["연료 종류"].append(fuel)
                        data_deficit["역내-추가 사용 가능(톤)"].append(round(tons_possible_in, 3))
                        data_deficit["역외-추가 사용 가능(톤)"].append(round(tons_possible_out, 3))

                df_deficit_table = pd.DataFrame(data_deficit)
                st.dataframe(df_deficit_table, use_container_width=True, hide_index=True)
        else:
                st.info("발생한 Deficit이 없습니다.")
                
                
        fossil_fuels = {
            "VLSFO": {"GFI": 91.60123, "LHV": 40500},
            "HSFO":  {"GFI": 91.60123, "LHV": 40500},
            "LSMGO": {"GFI": 90.63185, "LHV": 42700},
        }

        # ==================== 🔵 Surplus: 추가 화석 연료 사용량 ====================
        if surplus_rows:
            st.subheader("🟢 Surplus로 Pooling 가능한 화석연료 사용량 (톤)")


        # Surplus 기준은 "허용 최대 배출량"과 "현재 총배출량"의 차이로 계산
        allowed_emission = (standard_now * total_energy / 1_000_000) - total_emission  # tCO₂eq

        if allowed_emission > 0:
            pooling_table = {"연료 종류": [], "역내-추가 사용 가능(톤)": [], "역외-추가 사용 가능(톤)": []}

            for fuel, info in fossil_fuels.items():
                delta_ghg = info["GFI"] - standard_now
                if delta_ghg > 0:
                    allowed_energy = allowed_emission * 1_000_000 / delta_ghg  # MJ
                    tons_possible_in = allowed_energy / info["LHV"]  # 역내 톤수
                    tons_possible_out = tons_possible_in * 2         # 역외 톤수
                    pooling_table["연료 종류"].append(fuel)
                    pooling_table["역내-추가 사용 가능(톤)"].append(round(tons_possible_in, 3))
                    pooling_table["역외-추가 사용 가능(톤)"].append(round(tons_possible_out, 3))
                else:
                    pooling_table["연료 종류"].append(fuel)
                    pooling_table["역내-추가 사용 가능(톤)"].append(0.0)
                    pooling_table["역외-추가 사용 가능(톤)"].append(0.0)

            df_pooling = pd.DataFrame(pooling_table)
            st.dataframe(df_pooling, use_container_width=True, hide_index=True)
        else:
            st.info("Surplus가 없어 추가로 사용할 수 있는 화석연료가 없습니다.")


# 나머지 메뉴
#elif menu == "CII (준비 중)":
    #st.title("⚓ CII 계산기 (준비 중)")
#elif menu == "EU ETS (준비 중)":
    #st.title("💶 EU ETS 계산기 (준비 중)")


