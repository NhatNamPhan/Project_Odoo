# TEST CASE THỦ CÔNG — QUẢN LÝ ĐỒ ÁN TỐT NGHIỆP

**Module:** `quanly_datn`, Odoo 18, source đối chiếu `18.0.1.3.0`.

**Truy cập:** [http://localhost:8069/web/login?db=datn_db](http://localhost:8069/web/login?db=datn_db).

**Mục đích:** checklist để người dùng tự test. Các ô `NOT RUN` chưa được xác nhận PASS. Không suy ra mọi chức năng đã đúng từ các bộ kiểm thử tự động trước đó.

**Tổng cộng 106 mục:** 16 bước toàn luồng (mục 3), 79 ca chức năng/giao diện (mục 4), 6 tiêu chí cần xác minh thêm (mục 5), 5 ca API nâng cao (mục 6).

## 1. Quy ước và tài khoản

- **BCN:** thuộc nhóm Ban Chủ nhiệm Khoa / Giáo vụ, không chỉ dựa vào tên hiển thị Admin.
- **GVHD:** người được gán hướng dẫn đúng đề tài đang test; **HĐ:** thành viên hội đồng của đề tài.
- **New:** tạo mới. **Lưu:** nút lưu thủ công hình đám mây cạnh tên bản ghi hoặc chức năng lưu của Odoo. Tải lại trang để xác nhận dữ liệu đã lưu.
- Thanh trạng thái chỉ hiển thị tiến độ. Chuyển giai đoạn bằng các **nút nghiệp vụ** được nêu trong từng ca.
- Điền kết quả: `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`; ghi mã lỗi nếu FAIL. Không thực hiện được vì thiếu dữ liệu thì ghi BLOCKED.
- Với ca phân quyền, trường/nút/bản ghi bị ẩn hoặc chỉ đọc là kết quả hợp lệ. Không cần vượt giao diện; các ca gọi API trái quyền được để riêng ở mục 6.
- Dùng các hồ sơ trình duyệt khác nhau, hoặc đăng xuất rồi đăng nhập lại khi đổi vai trò. Hai tab thường cùng hồ sơ dùng chung phiên; nhiều cửa sổ ẩn danh cùng trình duyệt cũng có thể dùng chung phiên.

Tài khoản dưới đây lấy từ tài liệu/script dữ liệu mẫu, chưa xác nhận lại mật khẩu ở lần viết tài liệu này. Nếu đã đổi mật khẩu, dùng mật khẩu hiện tại. Hồ sơ mới tạo có mật khẩu ngẫu nhiên; quản trị viên phải đặt mật khẩu trước khi giao cho người test.

| Ký hiệu | Vai trò trong bộ test | Tài khoản mẫu | Mật khẩu mẫu nếu chưa đổi |
| --- | --- | --- | --- |
| BCN | Quản lý đợt, phân công và khóa điểm | `admin@ute.udn.vn` | `admin` |
| SV-A | Phan Hồ Nhật Nam | `nhatnam@sv.ute.udn.vn` | `123456` |
| SV-B | Nguyễn Quang Huy | `quanghuy@sv.ute.udn.vn` | `123456` |
| SV-C | Trần Thị Thu Hà; test từ chối đăng ký | `thuha@sv.ute.udn.vn` | `123456` |
| GV-HD | ThS. Nguyễn Thị Hà Quyên; gán hướng dẫn cả hai đề tài test | `haquyen@ute.udn.vn` | `123456` |
| HĐ-1 | PGS.TS. Lê Văn Bình; chủ tịch hội đồng test | `levanb@ute.udn.vn` | `123456` |
| HĐ-2 | TS. Trần Văn An; thư ký hội đồng test, không hướng dẫn đề tài test | `tranvana@ute.udn.vn` | `123456` |

## 2. Chuẩn bị dữ liệu

### 2.1. Bộ dữ liệu mới mỗi lần chạy

Chọn hậu tố `LAN01`; chạy lại toàn bộ thì đổi thành `LAN02` để tránh trùng mã và đăng ký. Tái sử dụng hồ sơ/tài khoản mẫu, tạo đăng ký vào đợt mới; không tạo lại hồ sơ mẫu.

| Dữ liệu | Giá trị đề nghị | Cách chuẩn bị |
| --- | --- | --- |
| Đợt chính | `TEST_DATN_LAN01`, tên Đợt kiểm thử LAN01 | BCN tạo ở Đợt Đồ Án → Đợt làm đồ án; niên khóa `2026 - 2027`, học kỳ 1, trọng số `30/20/50`; giữ Chuẩn bị mở đợt. |
| Đợt đối chứng | `TEST_KHAC_LAN01` | BCN tạo đợt khác để kiểm tra liên kết sai đợt. |
| Đăng ký A/B/C | A, B, C đăng ký đợt chính | Sau khi mở đăng ký, BCN duyệt A/B, từ chối C. |
| Đề tài A | `TEST_DT_A_LAN01`, tên Sản phẩm kiểm thử A | BCN gán đăng ký A đã duyệt, GVHD Hà Quyên. |
| Đề tài B | `TEST_DT_B_LAN01`, tên Sản phẩm kiểm thử B | BCN gán đăng ký B đã duyệt, GVHD cũng là Hà Quyên. |
| Báo cáo 1 | Kiểm thử — Đợt 1, thứ tự `1` | BCN tạo ở Đề Tài & Tiến Độ → Cấu hình đợt báo cáo; thuộc đợt chính; hạn nộp ngày mai. |
| Báo cáo 2 | Kiểm thử — Đợt 2, thứ tự `2` | Cùng đợt chính; hạn nộp hôm qua, có thể đánh dấu bản cuối. |
| Báo cáo đối chứng | Kiểm thử — Đợt khác | Thuộc đợt đối chứng. |
| Hội đồng | `TEST_HD_LAN01` | Cùng đợt và chuyên ngành với A/B; thêm HĐ-1 Chủ tịch và HĐ-2 Thư ký trong lúc Dự thảo. Hai SV mẫu thuộc Kỹ thuật phần mềm; xác nhận lại trong hồ sơ. |
| Lịch | Một ngày tương lai, giờ ví dụ `08:30`, địa điểm rõ ràng | Nhập qua giao diện; đối chiếu Calendar bằng cùng tài khoản/múi giờ. |
| Tệp thật | Một PDF/Word đọc được, một PNG/JPG | Tệp có nội dung nhận diện được. Không dùng tệp giả của script mẫu để kết luận trình đọc PDF hoạt động. |

### 2.2. Dữ liệu cũ chỉ để tham khảo

Đây là trạng thái đã quan sát trong phiên làm việc trước, có thể đổi do bạn thao tác:

| Bản ghi | Trạng thái đã quan sát | Lưu ý khi test |
| --- | --- | --- |
| `DATN_2026_HK2` | Đang thực hiện; 5 đăng ký đã duyệt | Không dùng để test đăng ký mới thành công. |
| `DATN_2027_HK1` | Chuẩn bị mở đợt | Chỉ bấm Mở đăng ký nếu muốn mở thật; checklist dưới dùng đợt TEST riêng. |
| `DT2026_01` | Chờ bảo vệ; 4 phiếu đã chấm; tổng `9,39`, Xuất sắc | Dùng đối chiếu kết quả mẫu, không sửa cho các ca lỗi. |
| `DT2026_02` | Đang thực hiện, chưa đủ phiếu | Xếp loại Chưa đủ điểm; số điểm hiện tại là tạm tính. |
| `DT2026_03` | Chờ bảo vệ, chưa đủ phiếu | Không hiện nút Gửi yêu cầu bảo vệ vì đã qua bước đó. |

## 3. Luồng kiểm thử nhanh từ đầu đến cuối

Chạy theo thứ tự. Với các nhánh lỗi ở mục 4, thực hiện tại giai đoạn tương ứng trước khi đi tiếp. Không bấm Kết thúc đợt khi vẫn còn ca cần đợt hoạt động.

| Mã | Vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| E2E-01 | BCN | Tạo đợt chính/đối chứng theo mục 2. Trên đợt chính bấm Mở đăng ký và xác nhận. | Thành Đang cho đăng ký đề tài. | NOT RUN |
| E2E-02 | SV-A/B/C | Mỗi tài khoản vào Đợt Đồ Án → Danh sách đăng ký → New, chọn chính mình và đợt chính, lưu. | Mỗi người có một đăng ký Chờ duyệt. | NOT RUN |
| E2E-03 | BCN | Duyệt đăng ký cho A/B; Từ chối cho C và xác nhận. | A/B đã duyệt, C bị từ chối. | NOT RUN |
| E2E-04 | BCN | Đề Tài & Tiến Độ → Đề tài tốt nghiệp → New. Tạo A/B, gán đúng đăng ký và Hà Quyên làm GVHD. | Đang thực hiện; tự hiện đúng sinh viên/đợt, xếp loại Chưa đủ điểm. | NOT RUN |
| E2E-05 | BCN | Tạo hai đợt báo cáo chính và một đối chứng. Trên đợt chính bấm Đóng đăng ký / Bắt đầu thực hiện, xác nhận. | Đợt chính thành Đang thực hiện đồ án. | NOT RUN |
| E2E-06 | SV-A/B | Mỗi người dùng Nộp báo cáo tiến độ → New, nộp tệp cho từng đợt 1 và 2. | 4 bài, mỗi cặp đề tài/đợt báo cáo có phiên bản 1, chờ duyệt. Đợt 1 không trễ; đợt 2 trễ. | NOT RUN |
| E2E-07 | GV-HD | Mở 4 bài, nhập nhận xét và bấm Đạt yêu cầu. | Cả 4 bài đạt; nhận xét còn khi tải lại. | NOT RUN |
| E2E-08 | SV-A/B | Mỗi người mở đề tài mình, bấm Gửi yêu cầu bảo vệ. | Thành Chờ GVHD xác nhận bảo vệ. | NOT RUN |
| E2E-09 | GV-HD | Bấm Xác nhận đủ điều kiện bảo vệ từng đề tài; nhập điểm GVHD A=`8`, B=`7`, lưu. Nếu cho điểm 0, bấm Xác nhận điểm GVHD để xác nhận đó là điểm 0 thực sự. | Chờ bảo vệ, cờ đồng ý bật; điểm lưu đúng, Đã nhập điểm GVHD bật. | NOT RUN |
| E2E-10 | BCN | Tạo hội đồng theo mục 2. Gán hội đồng cho A/B trên form đề tài, rồi Chốt lịch trên hội đồng. | Đã chốt lịch; tab thành viên/đề tài của hội đồng chỉ đọc. | NOT RUN |
| E2E-11 | BCN | Trên đợt chính bấm Bắt đầu bảo vệ, rồi trên hội đồng bấm Bắt đầu chấm / Tạo phiếu. | Đợt ở Giai đoạn bảo vệ; hội đồng Đang tiến hành chấm thi; có 4 phiếu chưa chấm: mỗi đề tài × mỗi thành viên. | NOT RUN |
| E2E-12 | HĐ-1 | Vào Phiếu chấm điểm. A: báo cáo `8`, đồ án `9`; B: `6`, `7`. Lưu, bấm Xác nhận điểm từng phiếu. | Hai phiếu đã chấm, có ngày chấm; A/B vẫn Chưa đủ điểm vì thiếu HĐ-2. | NOT RUN |
| E2E-13 | HĐ-2 | A: báo cáo `10`, đồ án `9`; B: `8`, `7`. Lưu và Xác nhận điểm. | A: TB báo cáo `9`, TB đồ án `9`, tổng `8,70`, Giỏi. B: TB báo cáo `7`, TB đồ án `7`, tổng `7,00`, Khá. | NOT RUN |
| E2E-14 | BCN | Trên hội đồng bấm Hoàn thành và khóa điểm, xác nhận. | Hội đồng hoàn thành; A/B Đã bảo vệ xong và đã khóa điểm. | NOT RUN |
| E2E-15 | SV-A/B; BCN | SV cập nhật link mã nguồn; vào Thư viện ảnh Showcase → New nộp ảnh. BCN mở từng đề tài, Xác nhận lưu chiểu. | A/B thành Đã nộp lưu chiểu. | NOT RUN |
| E2E-16 | BCN | Hoàn tất các ca cần đợt hoạt động, rồi bấm Kết thúc đợt. | Đợt thành Đã kết thúc đợt. | NOT RUN |

**Công thức:** tổng kết = GVHD × 30% + TB báo cáo hội đồng × 20% + TB đồ án hội đồng × 50%. TB báo cáo trong công thức lấy từ **phiếu chấm hội đồng**, không phải số bài tiến độ đã đạt. Dùng dấu thập phân phù hợp ngôn ngữ của tài khoản.

## 4. Các ca chi tiết và ca lỗi

Chạy ca tại giai đoạn ghi trong điều kiện. Sau khi thử nhập sai, **hủy thay đổi**, không để dữ liệu lỗi ảnh hưởng ca sau. Nếu đã vượt giai đoạn, tạo bộ mới với hậu tố khác.

### 4.1. Đăng nhập và giao diện

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-UI-01 | Tất cả tài khoản test | Đăng nhập lần lượt đúng mật khẩu, mở Quản Lý Đồ Án. | Vào được; đúng vai trò/dữ liệu, không lỗi server/OWL. | NOT RUN |
| TC-UI-02 | Chưa đăng nhập | Nhập sai mật khẩu một tài khoản test và đăng nhập. | Không tạo phiên; báo thông tin đăng nhập không đúng. | NOT RUN |
| TC-UI-03 | BCN | Mở từng nhóm menu, mở một form, quay lại bằng breadcrumb. | Danh sách/form tải được, quay lại đúng, không trang trắng/hộp lỗi. | NOT RUN |
| TC-UI-04 | BCN; danh sách đề tài | Tìm mã A; bật/tắt cột Đợt và Hội đồng trong bộ chọn cột. | Tìm đúng; cột tùy chọn hoạt động; đọc được mã, tên, điểm và trạng thái khi phóng to cửa sổ. | NOT RUN |
| TC-UI-05 | Có lịch hội đồng test | Chuyển Calendar tới tháng lịch test, mở sự kiện, đối chiếu form cùng tài khoản. | Cùng ngày/giờ/địa điểm theo múi giờ tài khoản. Không mặc định lịch mẫu cũ là 08:00. | NOT RUN |
| TC-UI-06 | Tất cả vai trò | Thu nhỏ cửa sổ, cuộn bảng/form, mở menu bị gom vào More. | Vẫn truy cập được nút, tab, trường bắt buộc; không bị lớp che cản thao tác. | NOT RUN |

### 4.2. Chuyên ngành, lớp và hồ sơ

Đường dẫn: **Tổ Chức & Người Dùng → Chuyên ngành / Lớp sinh hoạt / Sinh viên / Giảng viên**.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-ORG-01 | BCN | Tạo chuyên ngành `TEST_CN_LAN01`, rồi lớp `TEST_LOP_LAN01`, điền tên, niên khóa và chọn chuyên ngành mới. | Lưu được; lớp hiện ở tab danh sách lớp của chuyên ngành. | NOT RUN |
| TC-ORG-02 | BCN | Tạo chuyên ngành/lớp có mã trùng, điền đủ trường khác và lưu. | Bị chặn mã trùng; hủy bản ghi thử. | NOT RUN |
| TC-ORG-03 | BCN | Tạo SV có mã/email mới, nhập tên, chọn lớp test, lưu. | Chuyên ngành theo lớp và chỉ đọc; có tài khoản liên kết. Mật khẩu mới không mặc định là 123456. | NOT RUN |
| TC-ORG-04 | BCN | Tạo SV trùng MSSV nhưng email mới; tạo GV trùng mã nhưng email khác. | Mỗi ca bị chặn trùng mã, không sinh thêm hồ sơ hợp lệ. | NOT RUN |
| TC-ORG-05 | BCN | Tạo GV mã/email mới, đủ tên, chuyên ngành, học vị và hạn mức, lưu. | Có hồ sơ/tài khoản; GV hiện trong danh sách của chuyên ngành. | NOT RUN |
| TC-ORG-06 | BCN | Tạo hồ sơ với email đã là login khác, để trống Tài khoản liên kết, lưu. | Yêu cầu liên kết tài khoản hiện có; không tự lấy tài khoản đó cho hồ sơ mới. | NOT RUN |
| TC-ORG-07 | SV-A; GV-HD | Đổi số điện thoại của mình, lưu/tải lại. Thử sửa mã, email, lớp/chuyên ngành, tài khoản liên kết. | Chỉ số điện thoại sửa được. Ghi số cũ để khôi phục sau test. | NOT RUN |
| TC-ORG-08 | SV-A | Tìm/mở hồ sơ SV-B. | Không đọc được hồ sơ SV khác. GV có quyền đọc danh sách SV rộng hơn nên không dùng GV cho ca này. | NOT RUN |

### 4.3. Đợt đồ án và đăng ký

Đường dẫn: **Đợt Đồ Án → Đợt làm đồ án / Danh sách đăng ký**.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-DOT-01 | BCN; đợt mới | Điền đủ mã/tên/niên khóa/học kỳ rồi lưu. | Chuẩn bị mở đợt, hiện Mở đăng ký. | NOT RUN |
| TC-DOT-02 | BCN; chưa có điểm khóa | Thử `30/20/40`, rồi `-10/60/50`, mỗi lần lưu/hủy lỗi; thử `0/50/50`. | Hai bộ đầu bị chặn, bộ cuối hợp lệ. Khôi phục `30/20/50` trước test điểm. | NOT RUN |
| TC-DOT-03 | BCN | Nhập kết thúc bảo vệ trước bắt đầu và lưu. | Bị chặn; cùng ngày được phép theo ràng buộc hiện tại. | NOT RUN |
| TC-DOT-04 | BCN; Chuẩn bị | Bấm Mở đăng ký, hủy hộp thoại; kiểm tra. Bấm lại và xác nhận. | Hủy giữ trạng thái; xác nhận chuyển Đang cho đăng ký đề tài. | NOT RUN |
| TC-DOT-05 | SV-A đã đăng ký chính | Tạo thêm đăng ký A vào cùng đợt. | Chặn đăng ký trùng. | NOT RUN |
| TC-DOT-06 | SV-A; đợt đối chứng Chuẩn bị | Tạo đăng ký của mình vào đợt đối chứng. | Không lưu vì đợt chưa mở đăng ký. | NOT RUN |
| TC-DOT-07 | SV-A | Tạo đăng ký, thử chọn SV-B. | Không chọn/đọc được B hoặc không lưu được đăng ký hộ. | NOT RUN |
| TC-DOT-08 | SV-A; GV-HD | Mở đăng ký, tìm nút Duyệt đăng ký/Từ chối. | Không có thao tác duyệt cho vai trò này. | NOT RUN |
| TC-DOT-09 | BCN; C Chờ duyệt | Bấm Từ chối, xác nhận. | Thành Từ chối; các nút duyệt/từ chối không còn hiện. Hiện chưa có nút mở lại đăng ký bị từ chối. | NOT RUN |
| TC-DOT-10 | BCN; A đã giao đề tài | Thử đổi sinh viên hoặc đợt trên đăng ký A, lưu. | Bị chặn vì đã giao đề tài; hủy thay đổi. | NOT RUN |
| TC-DOT-11 | Sau khi đóng đăng ký | Dùng SV chưa đăng ký đợt đó tạo đăng ký mới. | Bị chặn do đợt đã đóng. Không dùng A/B để tránh lẫn lỗi trùng. | NOT RUN |
| TC-DOT-12 | BCN; Giai đoạn bảo vệ, HĐ chưa hoàn thành | Bấm Kết thúc đợt, xác nhận. | Bị chặn, yêu cầu hoàn thành hội đồng; trạng thái giữ nguyên. | NOT RUN |

### 4.4. Ngân hàng đề tài và giao đề tài

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-TOP-01 | BCN | Ngân hàng đề tài → New, chọn đợt/chuyên ngành chính, nguồn và người đề xuất, lưu; Duyệt đề tài. | Thành Đã duyệt (Có thể đăng ký). Tạo bản khác cho nhánh Từ chối. | NOT RUN |
| TC-TOP-02 | SV-A; GV-HD | Mở Ngân hàng đề tài, kiểm tra tạo/duyệt. | Theo ACL hiện tại hai vai trò chỉ đọc, không tạo hoặc duyệt đề xuất. | NOT RUN |
| TC-TOP-03 | BCN; trước khi giao A | Tạo đề tài, thử chọn đăng ký chưa duyệt/bị từ chối. | Bộ chọn chỉ gợi ý đăng ký đã duyệt; không giao cho đăng ký chưa duyệt. | NOT RUN |
| TC-TOP-04 | BCN; A đã có đề tài | Tạo đề tài mã mới nhưng cùng đăng ký A. | Chặn: mỗi đăng ký chỉ có một đề tài. | NOT RUN |
| TC-TOP-05 | BCN; đề tài chưa khóa | Thử chọn nguồn đề xuất chưa duyệt hoặc thuộc đợt đối chứng; sau đó chọn nguồn đã duyệt cùng đợt. | Không gợi ý nguồn sai đợt/chưa duyệt; nguồn đúng lưu được. | NOT RUN |
| TC-TOP-06 | SV-A | Sửa mô tả/link mã nguồn/demo của A, lưu/tải lại. Thử sửa tên/mã, GVHD, điểm, cờ duyệt. | Nội dung/link lưu được; trường quản lý chỉ đọc. | NOT RUN |
| TC-TOP-07 | SV-B | Tìm A hoặc mở đường dẫn A sao chép từ phiên SV-A. | Không truy cập được A; không yêu cầu thông báo phải nguyên văn một loại lỗi. | NOT RUN |

### 4.5. Cấu hình, nộp và duyệt báo cáo

Đường dẫn: **Đề Tài & Tiến Độ → Cấu hình đợt báo cáo / Nộp báo cáo tiến độ**.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-REP-01 | BCN | Tạo thứ tự `0`; rồi thử `1` đã có trong đợt chính. | 0 bị chặn; thứ tự trùng cùng đợt bị chặn. Thứ tự 1 ở đợt khác được phép. | NOT RUN |
| TC-REP-02 | SV-A; Đang thực hiện | New bài nộp, chọn A, thử tìm đợt báo cáo đối chứng. | Chỉ gợi ý đợt báo cáo cùng đợt đồ án. | NOT RUN |
| TC-REP-03 | SV-A; Đang thực hiện | Nhập tên/đợt, chỉ nhập URL, không đính kèm file rồi lưu. | Bị chặn thiếu tệp bắt buộc; URL không thay thế file. | NOT RUN |
| TC-REP-04 | SV-A; đã có bản 1 đợt 1 | New bài nộp sửa cho cùng A/đợt 1, không sửa bản cũ. | Tự thành phiên bản 2, chờ duyệt; giữ bản 1/phản hồi cũ. | NOT RUN |
| TC-REP-05 | GV-HD; bài chờ duyệt | Nhập phản hồi, Yêu cầu sửa và nộp lại; tải lại. Bài test khác: bấm Không đạt. | Lưu đúng phản hồi/trạng thái; không thay nội dung tệp SV đã nộp. | NOT RUN |
| TC-REP-06 | SV-A | Mở bài đã nộp, thử đổi file/đợt/phiên bản/phản hồi hoặc duyệt. | Không chỉnh sửa bài đã nộp, không có nút duyệt. Muốn sửa phải nộp bản mới khi Đang thực hiện. | NOT RUN |
| TC-REP-07 | HĐ-2 không là GVHD A | Tìm/mở bài A, thử duyệt. | Không đọc/duyệt được; quyền hội đồng không tự có quyền duyệt tiến độ. | NOT RUN |
| TC-REP-08 | SV-A; hạn 1 ngày mai, hạn 2 hôm qua | Nộp vào cả hai đợt; đối chiếu Nộp trễ. | Đợt 1 False, đợt 2 True theo ngày Việt Nam. Không yêu cầu tick phải màu đỏ. | NOT RUN |
| TC-REP-09 | GV-HD hoặc BCN | Tải tệp đã nộp, mở bằng ứng dụng đọc. | Đúng tên/nội dung tệp thật. Không dùng file mẫu giả để kết luận lỗi tải file. | NOT RUN |
| TC-REP-10 | SV-A; A Chờ xác nhận/Chờ bảo vệ | Tạo bài báo cáo mới cho A. | Bị chặn: chỉ nộp khi đề tài Đang thực hiện. | NOT RUN |

### 4.6. Điều kiện bảo vệ và nhánh từ chối

Chạy nhánh theo thứ tự: thiếu bài → bản mới chưa đạt → duyệt đủ → gửi → từ chối → cho bổ sung → gửi lại → xác nhận, trước khi chốt hội đồng.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-DEF-01 | SV-A; A Đang thực hiện, thiếu đợt đạt | Gửi yêu cầu bảo vệ. | Bị chặn, cần báo cáo đạt ở tất cả đợt; trạng thái không đổi. | NOT RUN |
| TC-DEF-02 | SV-A; bản cũ đạt, bản mới nhất đợt 1 chờ | Gửi yêu cầu bảo vệ. | Bị chặn dù bản cũ đạt; xét bản mới nhất từng đợt. | NOT RUN |
| TC-DEF-03 | SV-A; GVHD duyệt toàn bộ bản mới nhất | Gửi yêu cầu bảo vệ, tải lại. | Thành Chờ GVHD xác nhận bảo vệ; nút gửi biến mất. | NOT RUN |
| TC-DEF-04 | HĐ-1/HĐ-2; A chờ xác nhận | Mở A nếu có quyền đọc, tìm nút xác nhận/từ chối. | Không xác nhận thay GVHD; quyền đọc không đồng nghĩa quyền duyệt. | NOT RUN |
| TC-DEF-05 | GV-HD; A chờ xác nhận | Không đủ điều kiện → xác nhận. Sau đó Cho phép bổ sung báo cáo. | Đầu tiên Không được bảo vệ, cờ duyệt tắt; sau đó Đang thực hiện để SV nộp bổ sung. | NOT RUN |
| TC-DEF-06 | SV-A; bổ sung đủ bài đạt | Gửi lại; GVHD Xác nhận đủ điều kiện bảo vệ. | Thành Đủ điều kiện chờ bảo vệ, cờ đồng ý bật. | NOT RUN |

### 4.7. Hội đồng, phiếu chấm và khóa điểm

Đường dẫn: **Hội Đồng & Chấm Điểm → Hội đồng bảo vệ (Lịch Calendar) / Phiếu chấm điểm**.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-COU-01 | BCN; HĐ Dự thảo | Để thiếu thành viên hoặc đề tài rồi Chốt lịch. | Bị chặn, cần cả hai danh sách. | NOT RUN |
| TC-COU-02 | BCN; HĐ Dự thảo | Thêm cùng GV hai lần, lưu. | Chặn thành viên trùng. | NOT RUN |
| TC-COU-03 | BCN; đề tài chưa khóa | Thử gán HĐ khác đợt; thử HĐ cùng đợt khác chuyên ngành. | Khác đợt không được gợi ý; khác chuyên ngành không lưu được. | NOT RUN |
| TC-COU-04 | BCN; HĐ có A chưa được duyệt bảo vệ | Chốt lịch. | Bị chặn tới khi GVHD xác nhận A đủ điều kiện. | NOT RUN |
| TC-COU-05 | BCN; đã Chốt lịch | Xem tab thành viên/đề tài; chuyển đợt sang Giai đoạn bảo vệ rồi Bắt đầu chấm / Tạo phiếu. | Tab chỉ đọc, không nút thêm/xóa dòng; tạo đủ phiếu chưa có, không nhân đôi phiếu cũ. Chưa chuyển đợt sang bảo vệ thì bị chặn bắt đầu chấm. | NOT RUN |
| TC-COU-06 | HĐ-1 | Tìm hoặc mở đường dẫn phiếu HĐ-2 từ phiên riêng. | Không đọc/sửa được phiếu người khác. | NOT RUN |
| TC-COU-07 | HĐ-1; phiếu chưa khóa | Thử `-1`, `10,01` từng ô điểm, lưu/hủy lỗi; thử `0`, `10`. | Ngoài 0–10 bị chặn; 0/10 hợp lệ. Khôi phục điểm E2E trước xác nhận. | NOT RUN |
| TC-COU-08 | HĐ-1; chưa xác nhận | Nhập/lưu điểm, chưa xác nhận; BCN xem A. Sau đó HĐ-1 Xác nhận điểm. | Phiếu chưa chấm không vào TB; xác nhận mới tính. Thiếu HĐ-2 vẫn Chưa đủ điểm. | NOT RUN |
| TC-COU-09 | GV-HD; chưa khóa | Thử điểm GVHD `-0,1`, `11`, rồi nhập `8`. | Hai giá trị sai bị chặn, 8 lưu được. | NOT RUN |
| TC-COU-10 | BCN; thiếu phiếu đã chấm | Hoàn thành và khóa điểm. | Bị chặn; vẫn Đang tiến hành chấm thi, đề tài chưa bị khóa do thao tác thất bại. | NOT RUN |
| TC-COU-11 | BCN; đủ phiếu E2E | Đối chiếu TB/tổng/xếp loại A/B, hoàn thành HĐ. | A `9/9/8,70/Giỏi`; B `7/7/7,00/Khá`; hoàn thành khóa cả hai. | NOT RUN |
| TC-COU-12 | HĐ-1, GV-HD; đã hoàn thành | Thử sửa điểm/nhận xét phiếu và điểm GVHD. | Chỉ đọc hoặc bị chặn; dữ liệu chấm đã khóa không đổi. | NOT RUN |
| TC-COU-13 | BCN; đợt có điểm khóa | Đổi trọng số thành bộ vẫn tổng 100%, ví dụ `20/30/50`, lưu. | Bị chặn do có điểm khóa; hủy thay đổi. | NOT RUN |

### 4.8. Ảnh và lưu chiểu

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-ARC-01 | SV-A | Thư viện ảnh Showcase → New, chọn A, nhập tiêu đề, tải PNG/JPG thật, mô tả, lưu. | Ảnh hiện trong danh sách và tab ảnh của A khi tải lại. | NOT RUN |
| TC-ARC-02 | SV-B | Tìm/mở đường dẫn ảnh A, thử sửa. | Không truy cập/sửa được ảnh A. | NOT RUN |
| TC-ARC-03 | BCN; đã bảo vệ, thiếu link nguồn hoặc ảnh | Xác nhận lưu chiểu. | Bị chặn yêu cầu đủ link/ảnh. Chạy trước khi bổ sung dữ liệu thành công. | NOT RUN |
| TC-ARC-04 | BCN; đã bảo vệ, đủ link/ảnh | Xác nhận lưu chiểu. | Thành Đã nộp lưu chiểu, điểm giữ nguyên, nút xác nhận biến mất. | NOT RUN |

### 4.9. Thông báo và trạng thái đọc

Đường dẫn: **Thông Báo → Quản lý thông báo / Thông báo của tôi**. A/B đã duyệt đăng ký, C bị từ chối.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-NOT-01 | BCN | Tạo Thông báo TEST LAN01, chọn đợt chính, nội dung, lưu; xem Người nhận. | Có A/B, không tự thêm C; người gửi là tài khoản hiện tại. | NOT RUN |
| TC-NOT-02 | SV-A; BCN | A mở Thông báo của tôi → thông báo test → Đánh dấu đã đọc. BCN xem Người nhận. | A đã đọc, có ngày đọc; B chưa đọc giữ nguyên. | NOT RUN |
| TC-NOT-03 | SV-C | Tìm/mở thông báo chỉ gửi A/B. | Không đọc được. | NOT RUN |
| TC-NOT-04 | BCN | Đồng bộ người nhận hai lần, đếm dòng. Nếu có SV mới được duyệt sau khi đăng, đồng bộ thêm. | Không tạo trùng; thêm SV mới được duyệt. | NOT RUN |
| TC-NOT-05 | BCN; đã có người nhận | Đổi đợt thông báo sang đối chứng, lưu. | Bị chặn; hủy thay đổi. | NOT RUN |
| TC-NOT-06 | BCN; SV-A | BCN thêm tệp thật ở tab đính kèm, lưu; A mở thông báo và tải. | A tải được tệp đúng; người không nhận không truy cập được theo quyền. | NOT RUN |
| TC-NOT-07 | SV-A; GV-HD | Kiểm tra Quản lý thông báo và quyền tạo. | Không đăng thông báo chính thức. GVHD không tự là người nhận đợt: danh sách tự sinh hiện lấy SV đã duyệt. | NOT RUN |

### 4.10. Trao đổi tiến độ

Đường dẫn: **Thông Báo → Trao đổi tiến độ**. Chỉ gửi nội dung thử vào đề tài TEST.

| Mã | Điều kiện / vai trò | Các bước | Kết quả mong đợi | Kết quả thực tế |
| --- | --- | --- | --- | --- |
| TC-MSG-01 | SV-A | New → chọn A → nhập TEST LAN01: Em đã nộp báo cáo → lưu. | Người gửi A, mặc định chưa đọc. | NOT RUN |
| TC-MSG-02 | GV-HD | Mở tin A, Đánh dấu đã đọc; tạo tin phản hồi. | Tin A đã đọc; phản hồi có người gửi GVHD. | NOT RUN |
| TC-MSG-03 | SV-A; tin A đã được đọc | Sửa nội dung tin mình gửi, lưu/tải lại. | Nội dung đổi, trạng thái về chưa đọc. | NOT RUN |
| TC-MSG-04 | SV-A | Mở tin do GVHD gửi, thử sửa nội dung. | Không sửa được tin người khác; được đánh dấu đọc khi là người nhận. | NOT RUN |
| TC-MSG-05 | SV-B; HĐ-2 | Tìm/mở tin A hoặc thử gửi vào A. | Không truy cập/gửi được nếu không là SV thực hiện/GVHD. Vai trò HĐ không tự có quyền trao đổi tiến độ. | NOT RUN |
| TC-MSG-06 | SV-A | Lưu tin trống nội dung; mở tin do mình gửi, tìm nút đánh dấu đọc. | Không lưu được nội dung trống; nút tự đánh dấu tin mình đã đọc không hiện. | NOT RUN |

## 5. Hồi quy các điều kiện liên quan nhiều bước

TC-GAP-01 đến TC-GAP-04 đã được bổ sung điều kiện kiểm soát trong bản sửa luồng 18.0.1.3.0 và có ca kiểm thử tự động liên quan. Các ô bên dưới vẫn NOT RUN để bạn xác nhận thủ công. TC-GAP-05/06 là quy tắc chưa thống nhất, chưa được triển khai trong lần sửa luồng này.

| Mã | Cách thử trên dữ liệu TEST | Kết quả mong muốn | Kết quả thực tế |
| --- | --- | --- | --- |
| TC-GAP-01 | A chờ GVHD xác nhận; đổi bài mới nhất từ Đạt sang Cần sửa rồi thử xác nhận bảo vệ. | Kiểm tra lại điều kiện/thu hồi yêu cầu; không xác nhận khi bản mới nhất chưa đạt. | NOT RUN |
| TC-GAP-02 | Chưa nhập điểm GVHD A; chấm đủ phiếu HĐ, thử hoàn thành. Sau đó GVHD bấm Xác nhận điểm GVHD với điểm 0 và thử lại. | Lần đầu bị chặn thiếu điểm GVHD; sau xác nhận điểm 0 được coi là hợp lệ, không nhầm với chưa nhập. Điểm 0 trên dữ liệu cũ cần được GVHD xác nhận lại. | NOT RUN |
| TC-GAP-03 | HĐ đã chốt/đang chấm; thử đổi HĐ trên form đề tài, thêm thành viên qua đường dẫn khác hoặc đổi lịch. | Phân công/lịch/phiếu vẫn nhất quán theo quy trình đã chốt; không vượt khóa bằng màn hình khác. | NOT RUN |
| TC-GAP-04 | Đợt kết thúc; BCN thử tạo thêm đề tài/đợt báo cáo; SV thử nộp vào đề tài còn Đang thực hiện. | Có quy tắc đóng dữ liệu nhất quán, không chỉ đổi nhãn trạng thái. | NOT RUN |
| TC-GAP-05 | Gán số đề tài vượt hạn mức hướng dẫn của một GV test. | Nếu hạn mức là điều kiện bắt buộc thì phải chặn/cảnh báo; cần xác nhận chính sách. | NOT RUN |
| TC-GAP-06 | Lập HĐ trùng giờ/phòng hoặc trùng GV với HĐ khác. | Phát hiện xung đột nếu yêu cầu quản lý lịch; có Calendar không chứng minh đã chặn trùng lịch. | NOT RUN |

## 6. Ca nâng cao và phạm vi chưa triển khai

Các ca API dưới đây dành cho người biết Odoo/API và môi trường test riêng, không bắt buộc để hoàn thành kiểm thử thao tác giao diện. Không dùng Admin để chứng minh người dùng thường đã bị chặn.

| Mã | Kiểm tra nâng cao | Kết quả cần đạt | Kết quả thực tế |
| --- | --- | --- | --- |
| TC-API-01 | SV ghi trạng thái đề tài trực tiếp, bỏ qua nút yêu cầu bảo vệ. | Bị từ chối; không vượt điều kiện báo cáo. | NOT RUN |
| TC-API-02 | GV tạo/sửa phiếu người khác hoặc gán thành viên HĐ khác. | Bị từ chối kể cả gửi trực tiếp ID. | NOT RUN |
| TC-API-03 | Sửa user_id hồ sơ, giả người gửi tin, sửa ngày đọc của người khác. | Không chiếm hồ sơ; server xác định người gửi; không sửa trạng thái đọc người khác. | NOT RUN |
| TC-API-04 | Hai yêu cầu nộp đồng thời cùng đề tài/đợt báo cáo. | Không trùng phiên bản; nếu tranh chấp phải trả lỗi xử lý được, không mất bài đã nộp thành công. | NOT RUN |
| TC-API-05 | Nộp 23:59 và 00:01 giờ Việt Nam quanh hạn bằng dữ liệu có kiểm soát. | Trễ theo ngày Việt Nam, không lệch vì UTC/múi giờ người mở. | NOT RUN |

**Chưa triển khai để nghiệm thu:** tự động phân công giảng viên phản biện và xuất phiếu/báo cáo PDF QWeb. Không đánh dấu PASS dựa vào README. Tải file SV đã nộp không phải chức năng hệ thống xuất PDF.

**Chưa quy định chặt trong source:** loại/kích thước tệp, định dạng email/số điện thoại, số thành viên/cơ cấu bắt buộc của hội đồng, cấm GVHD chấm đề tài mình hướng dẫn. Nếu là tiêu chí nghiệm thu, cần thống nhất quy tắc rồi thêm ca cụ thể.

## 7. Mẫu ghi lỗi và hoàn tất

| Trường | Nội dung điền |
| --- | --- |
| Mã lỗi / mã test | Ví dụ BUG-01 / TC-DEF-02 |
| Ngày giờ / phiên bản | Thời điểm test, phiên bản module |
| Vai trò / tài khoản | Người test, vai trò thực tế |
| Dữ liệu | Mã đợt/đề tài/báo cáo/hội đồng |
| Bước tái hiện | Bắt đầu từ đâu, bấm gì, nhập gì |
| Mong đợi | Chép từ ca test hoặc mô tả yêu cầu |
| Thực tế | Thông báo lỗi, trạng thái trước/sau, ảnh do bạn chụp nếu có |
| Mức độ | Chặn luồng / Sai dữ liệu hoặc quyền / Giao diện |
| Test lại | Chưa sửa / Chờ test lại / PASS sau sửa |

Khi kết thúc, ghi tổng PASS/FAIL/BLOCKED/NOT RUN; khôi phục số điện thoại đã đổi, hủy chỉnh sửa chưa lưu. Giữ dữ liệu TEST để tái hiện lỗi hoặc dọn theo kế hoạch trên môi trường test. Không chạy lại script sinh dữ liệu mẫu để reset: script có thể ghi đè bản ghi mẫu đang dùng.

Script hồi quy dành cho người phát triển: [check_workflow.py](custom_addons/quanly_datn/data/check_workflow.py), [check_full_cycle.py](custom_addons/quanly_datn/data/check_full_cycle.py). Kết quả script không thay thế kiểm thử thủ công hoặc các tiêu chí ở mục 5.
