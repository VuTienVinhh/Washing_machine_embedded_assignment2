# Phân công và nội dung từng người

Đây là kế hoạch phân công để nhóm tiếp quản, kiểm tra và trình bày gói bài đã soạn. Mỗi người cần đọc code hoặc phần báo cáo mình phụ trách. Không dùng kế hoạch này để khẳng định nhóm đã lắp mạch hoặc chạy thử phần cứng.

| Thành viên | Phần chốt | File chính | Người review |
|---|---|---|---|
| Nguyễn Viết Tấn Vương, 2353345 | Yêu cầu, giả định, module, FSM, bảng chuyển trạng thái và luồng công việc | `report/sections/01_requirements.tex`, `02_design.tex`, `03_transitions.tex`; hình 01, 02, 04 | Vinh kiểm tra sơ đồ; Tướng đối chiếu với code |
| Nguyễn Lê Cao Tướng, 2353300 | C++ controller, debounce, timer, STOP, Arduino sketch và sơ đồ nối chân | `firmware/washing_controller/`; `report/sections/04_hardware.tex`, `05_software.tex`; hình 03 | Vương kiểm tra yêu cầu; Vinh chạy test |
| Vũ Tiến Vinh, 2353334 | Mô phỏng, kiểm thử, ảnh kết quả, ghép LaTeX, PDF, mục lục và gói nộp | `simulator/`, `tests/`, `evidence/`; `report/sections/06_tests.tex`, `07_evidence.tex`, `08_team_references.tex` | Tướng kiểm tra demo; Vương đọc báo cáo cuối |

## Nguyễn Viết Tấn Vương

Nội dung cần nắm:

1. Máy nhận xu 10, 20, 50 cent. Cộng dồn đến ít nhất 50 mới vào Ready.
2. Ready chỉ bắt đầu khi nhấn RUN. Xóa toàn bộ tiền, không trả tiền dư.
3. Năm trạng thái và ý nghĩa của đèn, wash enable, timer ở từng trạng thái.
4. PAUSE tắt wash enable nhưng không dừng đồng hồ. RUN tiếp tục cùng chu kỳ.
5. STOP lần đầu tăng bộ đếm; lần hai kết thúc. Hết 30 phút cũng kết thúc ở Running hoặc Paused.
6. Những quyết định không có trong đề được ghi là giả định, đặc biệt đèn khi Paused, khoảng cách giữa hai STOP và cách thoát Error.

Câu giải thích tiếng Anh có thể dùng:

> We use five states. Coins change the credit before a cycle starts. RUN starts the cycle only when there is enough money. PAUSE stops washing, but it does not stop the timer. The machine returns to standby after the time ends or after two STOP presses.

Tiêu chí xong: bảng yêu cầu, sơ đồ và code thống nhất; không có đường chuyển trạng thái làm khởi động lại đồng hồ khi resume.

## Nguyễn Lê Cao Tướng

Nội dung cần nắm:

1. `controller.h` là logic chính, không phụ thuộc Arduino. Sketch chỉ đọc và ghi chân.
2. `started_` chỉ được cập nhật khi bắt đầu chu kỳ đã trả tiền, không cập nhật khi resume.
3. Timer là `1800000 ms`; `uint32_t(now - started_)` xử lý được trường hợp đồng hồ quay vòng.
4. Debounce 30 ms tạo một sự kiện cho một lần nhấn. Giữ STOP không tính thành hai lần.
5. Ưu tiên fault rồi timeout rồi STOP. Khi đang Running, PAUSE được xử lý trước RUN.
6. Mỗi LED có điện trở 330 ohm. D10 chỉ là tín hiệu điều khiển driver, không cấp nguồn cho động cơ.
7. Các nút xu và lệnh Serial là bộ giả lập coin acceptor để demo. Không phải cảm biến xác thực tiền thật.

Câu giải thích tiếng Anh:

> The sketch reads the buttons and sends events to the controller. We use a nonblocking loop, so the timer and LEDs keep updating. The start time stays the same during pause and resume. Button debounce makes one held press count only once.

Tiêu chí xong: hiểu và chạy được code; nếu cần board thật thì Verify, Upload rồi thử đúng các trạng thái; ghi rõ board và công cụ đã dùng khi bổ sung kết quả.

## Vũ Tiến Vinh

Nội dung cần nắm:

1. Mở HTML để demo; không cần đăng nhập hoặc Internet.
2. Cho 20 + 50 cent, RUN: tiền từ 70 về 0, timer 30:00.
3. Tăng 8 phút, PAUSE: còn 22 phút. Tăng thêm 8 phút, RUN: còn 14 phút.
4. Tăng 14 phút: Standby. Test STOP hai lần ở chu kỳ mới.
5. Inject fault: Error, wash OFF, RLED blink; reset bench để thoát lỗi.
6. Phân biệt test phần mềm với test board. Ảnh mô phỏng không chứng minh đã lắp mạch.
7. Kiểm tra PDF có bìa, advisor, đúng tên và MSSV, mục lục, hình rõ, không vượt 10 trang.

Câu giải thích tiếng Anh:

> We tested the controller with a virtual clock. The tests cover payment, pause, resume, timeout, STOP and error handling. We also compare the browser model with the C++ controller. The saved results are software evidence. A board demonstration must be recorded separately if required.

Tiêu chí xong: demo chạy được; kết quả test có log; file PDF và ZIP mở được; không ghi kết quả phần cứng chưa làm.

## Lịch để còn hai ngày review

Đề được cung cấp không ghi deadline. Nếu nhóm có 7 ngày, dùng lịch sau; nếu ít hơn, gộp các ngày làm nhưng vẫn giữ hai ngày cuối.

| Ngày | Vương | Tướng | Vinh | Mốc chung |
|---|---|---|---|---|
| 1 | Chốt requirements và giả định | Đọc core, chốt input/output | Mở demo, kiểm tra sườn báo cáo | Cùng hiểu đúng đề |
| 2 | Kiểm tra FSM và bảng output | Kiểm tra timer và coin logic | Rà scenario test | Chốt thiết kế |
| 3 | Đối chiếu chuyển trạng thái với code | Kiểm tra STOP, debounce, sketch | Chạy test và demo | Có bản chạy được |
| 4 | Sửa giải thích thiếu | Kiểm tra nối chân; làm board nếu được yêu cầu | Lưu log và ảnh thật từ demo | Đủ bằng chứng phù hợp |
| 5 | Chốt phần Design | Chốt phần Implementation | Ghép và build PDF | Dừng thêm tính năng |
| 6 | Review code với Tướng | Review demo và kết quả của Vinh | Review yêu cầu, hình và PDF | Sửa lỗi kỹ thuật |
| 7 | Cùng diễn tập trình bày | Cùng kiểm tra bản cuối | Đóng gói và kiểm tra quy định nộp | Nộp sau vòng review cuối |

Không có deadline cụ thể nên lịch trên là kế hoạch tương đối, không phải ngày nộp do giảng viên công bố.
